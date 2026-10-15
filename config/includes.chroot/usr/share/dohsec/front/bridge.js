// Ponte do D'OH!Sec OS: troca os apps simulados do front pelos de verdade.
// So roda quando o front e servido pelo dohsec-api (window.DOHSEC_API existe); aberto como
// arquivo num navegador comum, o front continua no modo simulado.
(function () {
  'use strict';
  const CFG = window.DOHSEC_API;
  const OS = window.dohsecV18;
  if (!CFG || !OS || !OS.win) return;

  const esc = OS.esc;
  const timers = {};

  // ---------------------------------------------------------------- utilitarios
  async function api(caminho, corpo) {
    const opt = { headers: { 'X-DOHSEC-Token': CFG.token } };
    if (corpo !== undefined) {
      opt.method = 'POST';
      opt.headers['Content-Type'] = 'application/json';
      opt.body = JSON.stringify(corpo);
    }
    const r = await fetch(caminho, opt);
    const dados = await r.json();
    if (!r.ok) throw new Error(dados.erro || ('erro ' + r.status));
    return dados;
  }

  function aviso(titulo, msg) {
    if (OS.toast) OS.toast(titulo, msg);
  }

  // Efeitos com o mesmo som do esboco (dohBeep, Web Audio), so com o som ligado no botao da bandeja
  const SONS = {
    erro: [[220, 196, 174, 146], 0.045],
    acerto: [[262, 330, 392, 523], 0.04],
    conquista: [[392, 523, 659, 784, 659, 784], 0.04],
    promocao: [[262, 330, 392, 523, 392, 523, 659, 784], 0.05],
  };
  function som(tipo) {
    /* global audioOn, dohBeep */
    if (typeof audioOn === 'undefined' || !audioOn || typeof dohBeep !== 'function' || !SONS[tipo]) return;
    dohBeep(SONS[tipo][0], SONS[tipo][1]);
  }

  function existe(id) {
    return document.getElementById('win_' + id);
  }

  function janela(id, titulo, icone, html, opt) {
    const w = OS.win(id, titulo, icone, html, opt || {});
    if (w) w.classList.add('dohsec-real');
    return w;
  }

  // Atualiza o conteudo enquanto a janela estiver aberta
  function enquantoAberta(id, ms, fn) {
    clearInterval(timers[id]);
    timers[id] = setInterval(() => {
      if (!existe(id)) return clearInterval(timers[id]);
      const w = existe(id);
      if (w.style.display !== 'none') fn();
    }, ms);
  }

  function pre(texto) {
    return '<pre class="dohsec-pre">' + esc(texto || '(vazio)') + '</pre>';
  }

  function tamanho(b) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
  }

  // ---------------------------------------------------------------- Terminal
  function urlTerminal(pasta, acao) {
    return '/terminal?pasta=' + encodeURIComponent(pasta || '') + '&acao=' + encodeURIComponent(acao || '');
  }

  function abreTerminal(id, titulo, pasta, comando) {
    const w = existe(id);
    if (w) return OS.focusWin(w);
    janela(id, titulo, '💻',
      '<iframe class="dohsec-term" src="' + esc(urlTerminal(pasta, comando)) + '"></iframe>',
      { w: 'min(960px,94vw)', h: 'min(620px,80vh)' });
  }

  function terminal() {
    abreTerminal('terminal', 'Terminal', '', '');
  }

  // ---------------------------------------------------------------- Processos
  async function processos() {
    const id = 'processes';
    const pinta = async () => {
      let d;
      try { d = await api('/api/processos'); } catch (e) { return; }
      const corpo = d.processos.map(p =>
        '<tr><td>' + p.pid + '</td><td>' + esc(p.usuario) + '</td><td>' + p.cpu.toFixed(1) +
        '</td><td>' + p.mem.toFixed(1) + '</td><td title="' + esc(p.comando) + '">' + esc(p.nome) +
        '</td><td>' + (p.usuario === d.meu_usuario
          ? '<button class="xp-btn dohsec-mini" data-dohsec-kill="' + p.pid + '">Encerrar</button>' : '') +
        '</td></tr>').join('');
      const alvo = document.querySelector('#win_' + id + ' .dohsec-tabela tbody');
      if (alvo) alvo.innerHTML = corpo;
    };
    if (!existe(id)) {
      janela(id, 'Processos', '⚙️',
        '<h3>⚙️ Processos em execução</h3><p class="dohsec-dica">Ordenados por uso de CPU. ' +
        'Você só pode encerrar os seus; os do sistema pedem <code>sudo kill</code> no Terminal.</p>' +
        '<table class="dohsec-tabela"><thead><tr><th>PID</th><th>Usuário</th><th>CPU %</th>' +
        '<th>Mem %</th><th>Nome</th><th></th></tr></thead><tbody></tbody></table>');
    } else {
      OS.focusWin(existe(id));
    }
    await pinta();
    enquantoAberta(id, 3000, pinta);
  }

  async function encerra(pid) {
    try {
      const r = await api('/api/processos/encerrar', { pid: Number(pid) });
      aviso(r.ok ? 'Processo encerrado' : 'Não deu', r.ok ? 'PID ' + pid : r.erro);
    } catch (e) { aviso('Erro', e.message); }
  }

  // ---------------------------------------------------------------- Rede
  async function rede() {
    const d = await api('/api/rede');
    janela('network', 'Rede', '📡',
      '<h3>📡 Rede</h3>' +
      '<h4>Interfaces e endereços <code>ip -brief address</code></h4>' + pre(d.interfaces) +
      '<h4>Rotas <code>ip route</code></h4>' + pre(d.rotas) +
      '<h4>Portas escutando <code>ss -tlnp</code></h4>' + pre(d.escutando) +
      '<h4>Conexões <code>ss -tunap</code></h4>' + pre(d.conexoes) +
      '<h4>DNS <code>/etc/resolv.conf</code></h4>' + pre(d.dns) +
      '<button class="xp-btn" data-dohsec-app="network">Atualizar</button>');
  }

  // ---------------------------------------------------------------- Logs
  async function logs(fonte) {
    fonte = fonte || 'sistema';
    const d = await api('/api/logs?fonte=' + encodeURIComponent(fonte));
    const abas = [['sistema', 'Sistema'], ['auth', 'Logins e sudo'], ['erros', 'Avisos e erros'], ['kernel', 'Kernel']]
      .map(([f, n]) => '<button class="xp-btn dohsec-mini' + (f === fonte ? ' dohsec-ativo' : '') +
        '" data-dohsec-logs="' + f + '">' + n + '</button>').join(' ');
    janela('logs', 'Logs/Eventos', '📜',
      '<h3>📜 Logs do sistema</h3><p class="dohsec-dica">Os mesmos que você vê com ' +
      '<code>journalctl</code> no Terminal. As evidências dos casos ficam em <code>~/springfield</code>.</p>' +
      abas + pre(d.texto));
  }

  // ---------------------------------------------------------------- Mini SIEM
  function siem() {
    if (existe('siem')) return OS.focusWin(existe('siem'));
    janela('siem', 'Mini SIEM', '🛡️',
      '<h3>🛡️ Mini SIEM</h3><p class="dohsec-dica">Busca de verdade nos logs do sistema ' +
      '(<code>journalctl</code>), em <code>/var/log</code> e nas evidências dos casos (<code>~/springfield</code>).</p>' +
      '<div class="cli-row"><input id="dohsecSiemQ" placeholder="ex.: Failed password, sudo, svc_backup">' +
      '<button class="xp-btn" data-dohsec-siem="1">Buscar</button></div><div id="dohsecSiemOut"></div>');
    setTimeout(() => { const q = document.getElementById('dohsecSiemQ'); if (q) q.focus(); }, 50);
  }

  async function buscaSiem() {
    const q = (document.getElementById('dohsecSiemQ') || {}).value || '';
    const out = document.getElementById('dohsecSiemOut');
    if (!out) return;
    out.innerHTML = '<p class="dohsec-dica">Buscando…</p>';
    try {
      const d = await api('/api/siem?q=' + encodeURIComponent(q));
      if (d.erro) { out.innerHTML = '<p class="dohsec-dica">' + esc(d.erro) + '</p>'; return; }
      out.innerHTML = '<p class="dohsec-dica">' + d.total + ' resultado(s) para <b>' + esc(d.termo) + '</b></p>' +
        '<table class="dohsec-tabela"><thead><tr><th>Fonte</th><th>Evento</th></tr></thead><tbody>' +
        d.resultados.map(r => '<tr><td>' + esc(r.fonte.replace(/^.*\/springfield\//, '~/springfield/')) +
          '</td><td class="dohsec-mono">' + esc(r.linha) + '</td></tr>').join('') + '</tbody></table>';
    } catch (e) { out.innerHTML = '<p class="dohsec-dica">' + esc(e.message) + '</p>'; }
  }

  // ---------------------------------------------------------------- Permissoes
  async function permissoes() {
    const d = await api('/api/permissoes');
    janela('permissions', 'Permissões', '🔐',
      '<h3>🔐 Permissões</h3>' +
      '<h4>Quem sou eu <code>id</code></h4>' + pre(d.eu) +
      '<h4>Contas que podem entrar</h4><table class="dohsec-tabela"><thead><tr><th>Usuário</th>' +
      '<th>UID</th><th>Pasta</th><th>Shell</th></tr></thead><tbody>' +
      d.usuarios.map(u => '<tr><td>' + esc(u.nome) + '</td><td>' + u.uid + '</td><td>' + esc(u.home) +
        '</td><td>' + esc(u.shell) + '</td></tr>').join('') + '</tbody></table>' +
      '<h4>O que posso fazer como administrador <code>sudo -l</code></h4>' + pre(d.sudo) +
      '<h4>Minha pasta <code>ls -la ~</code></h4>' + pre(d.home) +
      '<h4>Programas com SUID (rodam com o poder do dono) <code>find -perm -4000</code></h4>' + pre(d.suid));
  }

  // ---------------------------------------------------------------- Updates
  async function updates() {
    janela('updates', 'Updates', '🧩', '<h3>🧩 Atualizações</h3><p class="dohsec-dica">Consultando…</p>');
    const d = await api('/api/updates');
    janela('updates', 'Updates', '🧩',
      '<h3>🧩 Atualizações</h3><p class="dohsec-dica">Lista do último <code>apt update</code>. ' +
      'Para buscar novidades e instalar, use o botão: ele abre o Terminal com o comando.</p>' +
      (d.pendentes.split('\n').filter(l => l.includes('/')).length
        ? pre(d.pendentes) : '<div class="os-good">✅ Tudo atualizado. Nenhum pacote pendente.</div>') +
      '<button class="xp-btn" data-dohsec-update="1">Atualizar o sistema no Terminal</button>');
  }

  // ---------------------------------------------------------------- Arquivos
  let pastaAtual = '';
  let mostraOcultos = false;

  async function arquivos(caminho) {
    const d = await api('/api/arquivos?caminho=' + encodeURIComponent(caminho || pastaAtual || ''));
    if (d.erro) return aviso('Arquivos', d.erro);
    pastaAtual = d.caminho;
    const itens = d.itens.filter(i => mostraOcultos || !i.oculto);
    janela('files', 'Arquivos', '🗂️',
      '<h3>🗂️ ' + esc(d.caminho) + '</h3>' +
      '<div class="dohsec-barra">' +
      '<button class="xp-btn dohsec-mini" data-dohsec-dir="' + esc(d.pai) + '">⬆ Subir</button> ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-dir="~">🏠 Pasta pessoal</button> ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-dir="~/springfield">🧪 Casos</button> ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-ocultos="1">' + (mostraOcultos ? 'Esconder' : 'Mostrar') +
      ' ocultos</button> ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-termaqui="' + esc(d.caminho) + '">💻 Terminal aqui</button>' +
      '</div><table class="dohsec-tabela"><thead><tr><th>Nome</th><th>Tamanho</th><th>Permissão</th><th></th></tr></thead><tbody>' +
      itens.map(i => '<tr class="dohsec-linha" data-dohsec-' + (i.pasta ? 'dir' : 'ver') + '="' +
        esc(d.caminho.replace(/\/$/, '') + '/' + i.nome) + '"><td>' + (i.pasta ? '📁 ' : '📄 ') + esc(i.nome) +
        '</td><td>' + (i.pasta ? '' : tamanho(i.tamanho)) + '</td><td class="dohsec-mono">' + i.modo +
        '</td><td>' + (i.pasta ? '' : '<button class="xp-btn dohsec-mini" title="Inspecionar" data-dohsec-inspecionar="' +
          esc(d.caminho.replace(/\/$/, '') + '/' + i.nome) + '">🔬</button>') +
        '</td></tr>').join('') + '</tbody></table>');
  }

  async function verArquivo(caminho) {
    const d = await api('/api/arquivo?caminho=' + encodeURIComponent(caminho));
    if (d.erro) return aviso('Arquivos', d.erro);
    janela('viewer', d.caminho.split('/').pop(), '📄',
      '<h3>📄 ' + esc(d.caminho) + '</h3>' +
      '<div class="dohsec-barra"><button class="xp-btn dohsec-mini" data-dohsec-inspecionar="' + esc(d.caminho) +
      '">🔬 Inspecionar este arquivo</button></div>' +
      (d.binario ? '<p class="dohsec-dica">Arquivo binário. Use <code>file</code>, <code>strings</code> ou ' +
        '<code>xxd</code> no Terminal.</p>' : '') +
      (d.cortado ? '<p class="dohsec-dica">Arquivo grande: mostrando só o começo. Use <code>less</code>.</p>' : '') +
      pre(d.texto));
  }

  // ---------------------------------------------------------------- Carreira na Usina
  // Estagiario -> Operador da Usina -> Supervisor de Seguranca -> Chefe de Seguranca ->
  // (Teste final do Sr. Burns) -> Assistente do Sr. Burns. Etapas liberam em ordem.
  let carreira = null;

  async function atualizaCarreira() {
    carreira = await api('/api/carreira');
    pintaCargo();
    return carreira;
  }

  function barra(feitos, total) {
    const pct = total ? Math.round(100 * feitos / total) : 0;
    return '<div class="dohsec-progresso"><div style="width:' + pct + '%"></div></div>';
  }

  function cartaoCaso(c) {
    const estado = !c.liberado ? '🔒' : (c.resolvido ? '✅' : (c.iniciado ? '🔎' : '🆕'));
    return '<div class="dohsec-caso' + (c.resolvido ? ' dohsec-ok' : '') + (c.liberado ? '' : ' dohsec-trancado') + '">' +
      '<b>' + estado + ' ' + c.n + '. ' + esc(c.titulo) + '</b> <span class="muted-mini">' + esc(c.nivel) + '</span>' +
      (c.liberado ? '<div class="dohsec-barra"><button class="xp-btn dohsec-mini" data-dohsec-caso="' + c.n + '">' +
        (c.resolvido ? 'Rever' : (c.iniciado ? 'Continuar' : 'Investigar')) + '</button></div>' : '') + '</div>';
  }

  function campoNome(k, onde) {
    return '<div class="cli-row dohsec-nome"><label><b>Seu nome no certificado:</b></label>' +
      '<input id="dohsecNome_' + onde + '" maxlength="34" value="' + esc(k.nome || '') + '" placeholder="digite seu nome">' +
      '<button class="xp-btn dohsec-mini" data-dohsec-nome="' + onde + '">Salvar</button></div>';
  }

  async function gravaNome(onde) {
    const campo = document.getElementById('dohsecNome_' + onde);
    const nome = campo ? campo.value.trim() : '';
    if (!nome) return aviso('Nome', 'Digite seu nome primeiro.');
    await api('/api/carreira/nome', { nome });
    const nick = document.getElementById('nick');
    if (nick) nick.value = nome;
    aviso('Nome salvo', nome);
    if (existe('goals')) await minhaCarreira();
    if (existe('certificate')) await certificado();
  }

  // Objetivos -> Minha carreira
  async function minhaCarreira() {
    await nomePendente;
    let k = await atualizaCarreira();
    const nick = document.getElementById('nick');
    if (!k.nome && nick && nick.value.trim()) {
      await salvaNome();
      k = await atualizaCarreira();
    }
    const proxima = k.etapas.find(e => e.liberada && e.feitos < e.total);
    const degraus = k.etapas.map(e => {
      const st = e.feitos === e.total && e.total ? '✅' : (e.liberada ? '▶️' : '🔒');
      return '<div class="dohsec-degrau' + (e.liberada ? '' : ' dohsec-trancado') + '">' +
        '<b>' + st + ' ' + esc(e.nome) + '</b> <span class="muted-mini">' + esc(e.sub) + '</span>' +
        '<span class="dohsec-conta">' + e.feitos + '/' + e.total + '</span>' + barra(e.feitos, e.total) +
        '<span class="muted-mini">Concluir ' + esc(e.recompensa) + '</span></div>';
    }).join('');
    const historico = k.promocoes.length
      ? '<ul>' + k.promocoes.map(p => '<li>' + esc(p.data) + ': ' + esc(k.icones[p.cargo] || '') + ' ' + esc(p.cargo) + '</li>').join('') + '</ul>'
      : '<p class="muted-mini">Nenhuma promocao ainda. Todo mundo comeca no cafezinho.</p>';
    janela('goals', 'Minha carreira', '🎯',
      '<div class="dohsec-ficha"><span class="dohsec-ficha-icone">' + esc(k.icone) + '</span><div>' +
      '<div class="muted-mini">Ficha funcional - Usina Nuclear de Springfield</div>' +
      '<h3>' + esc(k.nome || 'Funcionario sem nome') + '</h3>' +
      '<div>Cargo atual: <b>' + esc(k.cargo) + '</b></div>' +
      '<div class="muted-mini">' + k.feitos + '/' + k.total + ' casos concluidos</div></div></div>' +
      campoNome(k, 'carreira') +
      (proxima ? '<div class="os-good"><b>Proximo passo:</b> concluir <b>' + esc(proxima.nome) + '</b> (' +
        proxima.feitos + '/' + proxima.total + '): ' + esc(proxima.recompensa) + '. ' +
        '<button class="xp-btn dohsec-mini" data-dohsec-app="case">Abrir a Mesa do Incidente</button></div>'
        : '<div class="os-good"><b>Voce chegou ao topo:</b> Assistente do Sr. Burns. Eeexcelente.</div>') +
      faixaMedalhas(await api('/api/conquistas').catch(() => null)) +
      '<h4>Plano de carreira</h4>' + degraus +
      '<h4>Historico de promocoes</h4>' + historico,
      { w: 'min(760px,94vw)', h: 'min(660px,84vh)' });
  }

  // Mesa do Incidente -> casos da etapa atual
  async function mesa() {
    const d = await api('/api/lab');
    const k = d.carreira;
    const etapa = k.etapas.find(e => e.liberada && e.feitos < e.total) || k.etapas[k.etapas.length - 1];
    const casos = d.casos.filter(c => c.trilha === etapa.trilha);
    janela('case', 'Mesa do Incidente', '🚨',
      '<h3>🚨 Mesa do Incidente: ' + esc(etapa.nome) + '</h3>' +
      '<p class="dohsec-dica">Casos da sua etapa atual (' + etapa.feitos + '/' + etapa.total + '). ' +
      'Concluindo todos: ' + esc(etapa.recompensa) + '. As evidencias sao arquivos de verdade: ' +
      'investigue no Terminal com as Ferramentas.</p>' + barra(etapa.feitos, etapa.total) +
      casos.map(cartaoCaso).join(''),
      { w: 'min(760px,94vw)', h: 'min(640px,82vh)' });
  }

  // Laboratorio -> todas as etapas, com cadeado nas que faltam
  async function laboratorio() {
    const d = await api('/api/lab');
    let html = '<h3>🧪 Laboratorio Springfield</h3><p class="dohsec-dica">' + d.carreira.feitos + '/' + d.casos.length +
      ' concluidos. Cargo atual: <b>' + esc(d.carreira.cargo) + '</b>. As etapas liberam em ordem.</p>';
    d.trilhas.forEach(t => {
      const itens = d.casos.filter(c => c.trilha === t.id);
      if (!itens.length) return;
      html += '<h4>' + (t.liberada ? '' : '🔒 ') + esc(t.nome) + ' <span class="muted-mini">' + esc(t.sub) + ' (' +
        itens.filter(c => c.resolvido).length + '/' + itens.length + ')</span></h4>';
      html += itens.map(cartaoCaso).join('');
    });
    janela('lab', 'Laboratorio', '🧪', html, { w: 'min(760px,94vw)', h: 'min(640px,82vh)' });
  }

  async function abreCaso(n) {
    const r = await api('/api/lab/iniciar', { n: Number(n) });
    if (r.bloqueado) return aviso('🔒 Ainda nao', r.erro);
    const d = await api('/api/lab');
    const c = d.casos.find(x => x.n === Number(n));
    janela('caso_' + n, c.titulo, '🔎',
      '<div class="dohsec-barra">' +
      '<button class="xp-btn" data-dohsec-investigar="' + esc(r.pasta) + '">💻 Investigar no Terminal</button> ' +
      '<button class="xp-btn" data-dohsec-dir="' + esc(r.pasta) + '">🗂️ Ver arquivos</button> ' +
      '<button class="xp-btn" data-dohsec-app="tools">🧰 Ferramentas</button>' +
      '<button class="xp-btn" data-dohsec-relatorio="' + n + '">📝 Relatório</button></div>' +
      markdown(r.leiame) +
      '<h4>Sua resposta</h4><div class="cli-row"><input id="dohsecResp_' + n + '" placeholder="digite a resposta">' +
      '<button class="xp-btn" data-dohsec-responder="' + n + '">Responder</button>' +
      '<button class="xp-btn" data-dohsec-dica="' + n + '">Dica</button></div>' +
      '<div id="dohsecCasoOut_' + n + '">' +
      (c.dicas.length ? '<p class="dohsec-dica">💡 ' + c.dicas.map(esc).join('<br>💡 ') + '</p>' : '') +
      (c.resolvido ? aprendizado(c.aprendizado) : '') + '</div>',
      { w: 'min(860px,94vw)', h: 'min(680px,84vh)' });
  }

  function markdown(texto) {
    const inline = s => esc(s).replace(/\\\|/g, '|')
      .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
      .replace(/`([^`]+)`/g, '<code>$1</code>');
    const linhas = texto.split('\n');
    let html = '', i = 0;
    while (i < linhas.length) {
      const l = linhas[i];
      if (l.startsWith('|')) {
        const linhasTabela = [];
        while (i < linhas.length && linhas[i].startsWith('|')) {
          const cel = linhas[i].trim().replace(/^\||\|$/g, '').split(/(?<!\\)\|/).map(c => c.trim());
          if (!cel.every(c => /^-+$/.test(c))) linhasTabela.push(cel);
          i++;
        }
        html += '<table class="dohsec-tabela">' + linhasTabela.map((r, n) => '<tr>' +
          r.map(c => (n ? '<td>' : '<th>') + inline(c) + (n ? '</td>' : '</th>')).join('') + '</tr>').join('') + '</table>';
        continue;
      }
      if (l.startsWith('# ')) html += '<h3>' + inline(l.slice(2)) + '</h3>';
      else if (l.startsWith('## ')) html += '<h4>' + inline(l.slice(3)) + '</h4>';
      else if (l.startsWith('- ')) html += '<div class="dohsec-item">• ' + inline(l.slice(2)) + '</div>';
      else if (l.trim()) html += '<p>' + inline(l) + '</p>';
      i++;
    }
    return '<div class="dohsec-leiame">' + html + '</div>';
  }

  function aprendizado(itens) {
    return '<div class="os-good"><b>✅ Resolvido! O que aprendemos</b><ul>' +
      itens.map(i => '<li>' + esc(i) + '</li>').join('') + '</ul></div>';
  }

  async function dica(n) {
    const d = await api('/api/lab/dica', { n: Number(n) });
    if (d.bloqueado) return aviso('🔒 Ainda nao', d.erro);
    const out = document.getElementById('dohsecCasoOut_' + n);
    if (out) out.innerHTML = '<p class="dohsec-dica">💡 ' + d.dicas.map(esc).join('<br>💡 ') + '</p>';
  }

  async function responder(n) {
    const campo = document.getElementById('dohsecResp_' + n);
    const r = await api('/api/lab/responder', { n: Number(n), resposta: campo ? campo.value : '' });
    if (r.bloqueado) return aviso('🔒 Ainda nao', r.erro);
    const out = document.getElementById('dohsecCasoOut_' + n);
    if (!r.certo) {
      som('erro');
      return aviso("D'oh!", 'Nao e isso. Tente de novo ou peca uma dica.');
    }
    som(r.promocao ? 'promocao' : 'acerto');
    aviso('Mmm... resolvido!', 'Caso ' + n + ' concluido');
    if (out) out.innerHTML = aprendizado(r.aprendizado);
    await atualizaCarreira();
    for (const id of ['goals', 'case', 'lab']) {
      if (existe(id)) await window.DOHSEC_REAL[id]();
    }
    if (r.promocao) promocao(r);
  }

  function promocao(r) {
    janela('promocao', 'Memorando interno', '📨',
      '<div class="dohsec-memo"><div class="muted-mini">DE: Waylon Smithers | PARA: ' +
      esc((carreira && carreira.nome) || 'Funcionario') + ' | ASSUNTO: Promocao</div>' +
      '<div class="dohsec-memo-cargo">' + esc(r.icone) + ' ' + esc(r.promocao) + '</div>' +
      '<p>' + esc(r.memorando) + '</p>' +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-app="certificate">🏆 Ver certificado</button>' +
      '<button class="xp-btn" data-dohsec-app="goals">🎯 Minha carreira</button></div></div>',
      { w: 'min(560px,94vw)', h: 'min(380px,70vh)' });
  }

  // Certificado do cargo atual (desenhado em canvas, salvo como PNG)
  async function certificado() {
    const k = await atualizaCarreira();
    k.medalhas = await api('/api/conquistas').catch(() => null);
    janela('certificate', 'Certificado', '🏆',
      campoNome(k, 'certificado') +
      '<canvas id="dohsecCert" width="1200" height="800" class="dohsec-cert"></canvas>' +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-salvar-cert="1">💾 Salvar PNG</button></div>',
      { w: 'min(860px,94vw)', h: 'min(680px,86vh)' });
    desenhaCertificado(k);
  }

  function desenhaCertificado(k) {
    const cv = document.getElementById('dohsecCert');
    if (!cv) return;
    const g = cv.getContext('2d');
    g.fillStyle = '#fff6d7'; g.fillRect(0, 0, 1200, 800);
    g.strokeStyle = '#5b3518'; g.lineWidth = 18; g.strokeRect(24, 24, 1152, 752);
    g.strokeStyle = '#ffd84d'; g.lineWidth = 6; g.strokeRect(48, 48, 1104, 704);
    g.textAlign = 'center'; g.fillStyle = '#171717';
    g.font = 'bold 30px "Share Tech Mono", monospace';
    g.fillText('USINA NUCLEAR DE SPRINGFIELD - BE SAFE INC.', 600, 130);
    g.font = 'bold 64px "DejaVu Sans", sans-serif';
    g.fillText('Certificado de Cargo', 600, 230);
    g.font = '28px "DejaVu Sans", sans-serif';
    g.fillText('Certificamos que', 600, 310);
    g.font = 'bold 52px "DejaVu Sans", sans-serif'; g.fillStyle = '#2f7df6';
    g.fillText(k.nome || 'Funcionario sem nome', 600, 390);
    g.font = '28px "DejaVu Sans", sans-serif'; g.fillStyle = '#171717';
    g.fillText('ocupa o cargo de', 600, 450);
    g.font = 'bold 50px "DejaVu Sans", sans-serif'; g.fillStyle = '#ff5fb7';
    g.fillText((k.icone || '') + ' ' + k.cargo, 600, 530);
    g.font = '24px "DejaVu Sans", sans-serif'; g.fillStyle = '#5b3518';
    g.fillText(k.feitos + ' de ' + k.total + ' casos resolvidos com ferramentas reais do Debian', 600, 590);
    const m = k.medalhas;
    if (m && m.ganhas) {
      const icones = m.conquistas.filter(x => x.ganha).map(x => x.icone);
      g.font = '22px "DejaVu Sans", sans-serif';
      g.fillText('Conquistas: ' + m.ganhas + ' de ' + m.total, 600, 635);
      g.font = '30px "Noto Color Emoji", "DejaVu Sans", sans-serif';
      g.fillText(icones.slice(0, 18).join(' ') + (icones.length > 18 ? ' ...' : ''), 600, 675);
    }
    g.font = '24px "DejaVu Sans", sans-serif';
    const ultima = k.promocoes.length ? k.promocoes[k.promocoes.length - 1].data : new Date().toISOString().slice(0, 10);
    g.fillText('Emitido em ' + ultima + '  -  Ass.: C. M. Burns (por W. Smithers)', 600, 725);
  }

  function salvaCertificado() {
    const cv = document.getElementById('dohsecCert');
    if (!cv) return;
    const a = document.createElement('a');
    a.href = cv.toDataURL('image/png');
    a.download = 'certificado-dohsec.png';
    a.click();
  }

  // Ferramentas reais por etapa
  const FERRAMENTAS = [
    ['Estagiario', [['ls / cd / pwd', 'navegar pelas pastas'], ['cat / less', 'ler arquivos'], ['grep', 'procurar texto'],
      ['wc / cut / sort / uniq', 'contar e filtrar'], ['find', 'achar arquivos'], ['tar', 'empacotar e extrair'], ['man', 'manual de tudo']]],
    ['Operador da Usina', [['id / whoami', 'quem sou eu'], ['chmod / ls -l', 'permissoes'], ['sha256sum', 'conferir hash'],
      ['file / xxd', 'tipo real de um arquivo'], ['strings', 'texto escondido em binarios'], ['systemctl / journalctl', 'servicos e logs'],
      ['ss / ip', 'rede e portas'], ['which / type', 'qual programa roda']]],
    ['Supervisor de Seguranca', [['jq', 'filtrar JSON'], ['tshark', 'analisar capturas de rede'], ['wireshark', 'capturas de rede (grafico)', 'wireshark'],
      ['tcpdump', 'capturar trafego'], ['Captura de Rede (app)', 'grava e resume o trafego em 1 clique'], ['yara', 'regras de deteccao'], ['awk', 'colunas de logs']]],
    ['Chefe de Seguranca', [['exiftool', 'metadados'], ['binwalk', 'arquivos dentro de arquivos'], ['sleuthkit (fls, icat)', 'forense de disco'],
      ['foremost', 'recuperar arquivos'], ['aide', 'integridade'], ['ufw / nft', 'firewall'], ['ausearch', 'auditoria (auditd)'],
      ['lynis', 'auditoria de endurecimento'], ['suricata', 'IDS'],
      ['Inspetor de Arquivos', 'laudo com file, strings, exiftool, binwalk, yara e clamscan juntos']]],
    ['Assistente do Sr. Burns (Teste final)', [['grep / less', 'cabecalhos do e-mail e o proxy.log'],
      ['tshark -q -z conv,ip', 'quem mandou dados para fora'], ['wireshark', 'a mesma captura no grafico', 'wireshark'],
      ['comm / diff', 'comparar servicos com a lista oficial'], ['systemctl list-unit-files', 'servicos instalados'],
      ['systemctl disable --now', 'remover persistencia (na vida real)'], ['ufw deny', 'bloquear o IP do atacante']]],
  ];

  function ferramentas() {
    janela('tools', 'Ferramentas', '🧰',
      '<h3>🧰 Ferramentas reais</h3><p class="dohsec-dica">Tudo instalado de verdade (Debian). Use no Terminal; ' +
      'as graficas abrem em janela propria. Dica: <code>man NOME</code> mostra o manual de qualquer uma.</p>' +
      FERRAMENTAS.map(([cargo, lista]) => '<h4>' + esc(cargo) + '</h4><table class="dohsec-tabela"><tbody>' +
        lista.map(([nome, oque, gui]) => '<tr><td class="dohsec-mono"><b>' + esc(nome) + '</b></td><td>' + esc(oque) +
          '</td><td>' + (gui ? '<button class="xp-btn dohsec-mini" data-dohsec-abrir="' + gui + '">Abrir</button>' : '') +
          '</td></tr>').join('') + '</tbody></table>').join('') +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-app="terminal">💻 Abrir o Terminal</button></div>',
      { w: 'min(760px,94vw)', h: 'min(640px,82vh)' });
  }

  async function abrePrograma(nome) {
    const r = await api('/api/abrir', { programa: nome });
    aviso(r.ok ? 'Abrindo' : 'Nao deu', r.ok ? nome + ' vai abrir em uma janela' : r.erro);
  }

  // Cargo no menu Iniciar e na barra das janelas, no lugar da trilha simulada do esboco
  const TRILHAS_ESBOCO = ['SOC / Blue Team', 'SysAdmin Linux Seguro', 'Windows / AD', 'DFIR / Resposta', 'Red Team / Pentest Ético'];
  function pintaCargo() {
    if (!carreira) return;
    const rotulo = carreira.icone + ' ' + carreira.cargo;
    document.querySelectorAll('#startmenu .muted-mini, .win-statusbar span').forEach(el => {
      const texto = el.textContent.trim();
      if (el.dataset.dohsecCargo || TRILHAS_ESBOCO.includes(texto)) {
        el.dataset.dohsecCargo = '1';
        if (texto !== rotulo) el.textContent = rotulo;
      }
    });
  }

  // Relogio real na bandeja (o do esboco e enfeite)
  function relogio() {
    const el = document.getElementById('clock');
    if (!el) return;
    const d = new Date();
    const dois = n => String(n).padStart(2, '0');
    el.innerHTML = dois(d.getHours()) + ':' + dois(d.getMinutes()) + '<br>' +
      dois(d.getDate()) + '/' + dois(d.getMonth() + 1) + '/' + d.getFullYear();
  }

  // Login: a ficha substitui a escolha de trilha simulada
  async function login() {
    const k = await atualizaCarreira().catch(() => null);
    if (!k) return;
    const nick = document.getElementById('nick');
    if (nick && k.nome) nick.value = k.nome;
    const chips = document.getElementById('chips');
    if (chips && chips.parentElement && !document.getElementById('dohsecFichaLogin')) {
      chips.parentElement.style.display = 'none';
      const ficha = document.createElement('div');
      ficha.id = 'dohsecFichaLogin';
      ficha.className = 'dohsec-ficha-login';
      ficha.innerHTML = '<div style="font-weight:900;font-size:13px;margin-bottom:6px">Sua ficha na Usina</div>' +
        '<div class="dohsec-ficha"><span class="dohsec-ficha-icone">' + esc(k.icone) + '</span><div><b>' + esc(k.cargo) +
        '</b><div class="muted-mini">' + k.feitos + '/' + k.total + ' casos concluidos</div></div></div>';
      chips.parentElement.parentElement.insertBefore(ficha, chips.parentElement);
    }
    const missao = document.querySelector('#login .mission');
    if (missao && !missao.dataset.dohsec) {
      missao.dataset.dohsec = '1';
      missao.innerHTML = '<b style="font-size:14px">🎯 Carreira na Usina</b>' +
        '<ol style="font-size:13px;line-height:1.7;margin:10px 0;padding-left:20px">' +
        '<li>🍩 <b>Estagiario</b>: aprenda o terminal</li><li>🔧 <b>Operador da Usina</b>: o sistema por dentro</li>' +
        '<li>🛡️ <b>Supervisor de Seguranca</b>: logs, trafego e deteccao</li>' +
        '<li>🔬 <b>Chefe de Seguranca</b>: forense e endurecimento</li>' +
        '<li>👔 <b>Teste final do Sr. Burns</b> para virar <b>Assistente do Sr. Burns</b></li></ol>' +
        '<p class="small" style="background:#fff8dc;border:1px solid #ddc;border-radius:4px;padding:8px;margin:0">' +
        'Tudo aqui e de verdade: Linux, Terminal e ferramentas reais. Seu progresso fica salvo.</p>';
    }
  }

  let nomePendente = Promise.resolve();
  async function salvaNome() {
    const nick = document.getElementById('nick');
    if (nick && nick.value.trim()) await api('/api/carreira/nome', { nome: nick.value.trim() }).catch(() => {});
    atualizaCarreira().catch(() => {});
  }

  // ---------------------------------------------------------------- Painel do Sr. Burns
  // Saude de seguranca da propria maquina: nota, humor do Sr. Burns e o que corrigir
  async function painelBurns() {
    const d = await api('/api/burns');
    const cor = d.nota >= 90 ? 'var(--green)' : (d.nota >= 70 ? 'var(--blue)' : (d.nota >= 40 ? 'var(--orange)' : 'var(--red)'));
    const icone = { ok: '✅', alerta: '⚠️', risco: '🚨' };
    const itens = d.itens.map(i => '<div class="dohsec-check dohsec-' + i.nivel + '">' +
      '<div><b>' + icone[i.nivel] + ' ' + esc(i.titulo) + '</b><div class="muted-mini">' + esc(i.detalhe) + '</div>' +
      (i.ok ? '' : '<div class="dohsec-como">Como corrigir: <code>' + esc(i.como) + '</code></div>') + '</div>' +
      (i.corrigivel ? '<button class="xp-btn dohsec-mini" data-dohsec-corrigir="' + esc(i.chave) + '">Corrigir</button>' : '') +
      '</div>').join('');
    janela('burns', 'Painel do Sr. Burns', '👔',
      '<div class="dohsec-burns-topo"><div class="dohsec-nota" style="border-color:' + cor + ';color:' + cor + '">' +
      d.nota + '</div><div><div class="dohsec-humor">"' + esc(d.humor) + '"</div>' +
      '<div class="muted-mini">' + esc(d.frase) + '</div></div></div>' +
      '<p class="dohsec-dica">Verificacoes reais desta maquina. Corrija os itens e veja a nota subir.</p>' + itens +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-app="burns">🔄 Verificar de novo</button>' +
      '<button class="xp-btn" data-dohsec-app="terminal">💻 Abrir o Terminal</button></div>',
      { w: 'min(780px,94vw)', h: 'min(680px,86vh)' });
  }

  async function corrigeBurns(chave) {
    const r = await api('/api/burns/corrigir', { chave });
    aviso(r.ok ? 'Corrigido' : 'Nao deu', r.ok ? 'O Sr. Burns anotou.' : r.erro);
    if (r.ok) painelBurns();
  }

  // Confirmacao no visual do front (sem a caixa padrao do navegador)
  function confirma(pergunta) {
    return new Promise(resolve => {
      janela('confirma', 'Confirmar', '❓',
        '<p class="dohsec-pergunta">' + esc(pergunta) + '</p><div class="dohsec-barra">' +
        '<button class="xp-btn" data-dohsec-resposta="sim">Sim</button>' +
        '<button class="xp-btn" data-dohsec-resposta="nao">Cancelar</button></div>',
        { w: 'min(420px,90vw)', h: '190px' });
      respostaPendente = v => {
        const w = existe('confirma');
        if (w) w.remove();
        const tarefa = document.getElementById('task_confirma');
        if (tarefa) tarefa.remove();
        resolve(v);
      };
    });
  }
  let respostaPendente = null;

  // ---------------------------------------------------------------- Inspetor de Arquivos
  // Laudo de um arquivo com ferramentas reais (file, strings, exiftool, binwalk, yara, clamscan).
  // O arquivo nunca e executado.
  async function inspetor(caminho) {
    const sugestoes = await api('/api/arquivos?caminho=' + encodeURIComponent('~/Downloads'))
      .then(d => (d.itens || []).filter(i => !i.pasta).slice(0, 8).map(i => d.caminho + '/' + i.nome))
      .catch(() => []);
    janela('inspector', 'Inspetor de Arquivos', '🔬',
      '<h3>🔬 Inspetor de Arquivos</h3><p class="dohsec-dica">Analisa um arquivo com as ferramentas reais ' +
      '(<code>file</code>, <code>strings</code>, <code>exiftool</code>, <code>binwalk</code>, <code>yara</code>, ' +
      '<code>clamscan</code>) e da um laudo. <b>O arquivo nunca e executado.</b> Tambem da para abrir pelo ' +
      'botao 🔬 no app Arquivos.</p>' +
      '<div class="cli-row"><input id="dohsecInspQ" placeholder="caminho do arquivo, ex.: ~/Downloads/fatura.pdf" value="' +
      esc(caminho || '') + '"><button class="xp-btn" data-dohsec-inspecionar="campo">Inspecionar</button></div>' +
      (sugestoes.length ? '<div class="dohsec-barra"><span class="muted-mini">Em Downloads:</span>' +
        sugestoes.map(s => '<button class="xp-btn dohsec-mini" data-dohsec-inspecionar="' + esc(s) + '">' +
          esc(s.split('/').pop()) + '</button>').join('') + '</div>' : '') +
      '<div id="dohsecInspOut"></div>',
      { w: 'min(860px,94vw)', h: 'min(700px,86vh)' });
    setTimeout(() => { const q = document.getElementById('dohsecInspQ'); if (q) q.focus(); }, 50);
    if (caminho) inspeciona(caminho);
  }

  async function inspeciona(caminho) {
    if (caminho === 'campo') caminho = (document.getElementById('dohsecInspQ') || {}).value || '';
    caminho = caminho.trim().replace(/^~/, '/home/' + (document.body.dataset.u || ''));
    if (!caminho) return aviso('Inspetor', 'Digite o caminho de um arquivo.');
    if (!existe('inspector')) return inspetor(caminho);
    const out = document.getElementById('dohsecInspOut');
    const campo = document.getElementById('dohsecInspQ');
    if (campo) campo.value = caminho;
    out.innerHTML = '<p class="dohsec-dica">🔬 Analisando... (antivirus e binwalk podem levar alguns segundos)</p>';
    const d = await api('/api/inspecionar?caminho=' + encodeURIComponent(caminho));
    if (d.erro) { out.innerHTML = '<p class="dohsec-dica">' + esc(d.erro) + '</p>'; return; }
    const veredito = {
      ok: ['🟢', 'Tranquilo', 'Nada estranho encontrado.'],
      alerta: ['🟡', 'Atencao', 'Tem pontos que merecem cuidado.'],
      risco: ['🔴', 'Suspeito', 'Nao abra nem execute. Investigue antes.'],
    }[d.veredito];
    const icone = { risco: '🔴', alerta: '🟡' };
    const linha = (rotulo, valor) => '<tr><th>' + esc(rotulo) + '</th><td class="dohsec-mono">' + esc(valor) + '</td></tr>';
    out.innerHTML =
      '<div class="dohsec-veredito dohsec-v-' + d.veredito + '"><span>' + veredito[0] + '</span><div><b>' +
      veredito[1] + '</b>: ' + esc(d.nome) + '<div class="muted-mini">' + veredito[2] + '</div></div></div>' +
      (d.achados.length ? '<h4>O que chamou atencao</h4>' + d.achados.map(a =>
        '<div class="dohsec-achado">' + icone[a.nivel] + ' ' + esc(a.texto) + '</div>').join('') : '') +
      '<h4>Identidade</h4><table class="dohsec-tabela dohsec-laudo">' +
      linha('Tipo real (file)', d.tipo) + linha('MIME', d.mime) + linha('Tamanho', tamanho(d.tamanho)) +
      linha('Arquivo', d.stat) + linha('SHA-256', d.sha256) + linha('MD5', d.md5) + '</table>' +
      '<h4>Textos encontrados (strings: ' + d.strings_total + ' trechos)</h4>' +
      (d.destaques.length ? d.destaques.map(x => '<div><b>' + esc(x.tipo) + ':</b> ' +
        x.valores.map(v => '<code>' + esc(v) + '</code>').join(' ') + '</div>').join('')
        : '<p class="muted-mini">Nenhum link, IP, e-mail ou senha nos textos.</p>') +
      '<h4>Metadados (exiftool)</h4>' + (d.metadados.length ? pre(d.metadados.join('\n')) : '<p class="muted-mini">Sem metadados relevantes.</p>') +
      '<h4>Arquivos embutidos (binwalk)</h4>' + (d.embutidos.length ? pre(d.embutidos.join('\n')) : '<p class="muted-mini">Nenhuma assinatura encontrada.</p>') +
      '<h4>Regras YARA</h4>' + (d.yara.length ? d.yara.map(r => '<div>🎯 <b>' + esc(r.regra) + '</b>: ' + esc(r.descricao) + '</div>').join('')
        : '<p class="muted-mini">Nenhuma regra bateu.</p>') +
      '<h4>Antivirus (ClamAV)</h4><p>' + esc(d.antivirus) + '</p>' +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-termaqui="' + esc(d.caminho.replace(/\/[^/]*$/, '')) +
      '">💻 Investigar no Terminal</button></div>';
  }

  // ---------------------------------------------------------------- Captura de Rede em 1 clique
  async function captura() {
    const d = await api('/api/capturas');
    const lista = (itens, vazio) => itens.length ? itens.map(c =>
      '<div class="dohsec-cap"><span class="dohsec-mono">' + esc(c.nome) + '</span>' +
      '<span><button class="xp-btn dohsec-mini" data-dohsec-analisar="' + esc(c.caminho) + '">Analisar</button> ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-wireshark="' + esc(c.caminho) + '">🦈 Wireshark</button></span></div>'
    ).join('') : '<p class="muted-mini">' + vazio + '</p>';
    janela('capture', 'Captura de Rede', '🦈',
      '<h3>🦈 Captura de Rede</h3><p class="dohsec-dica">Grava o trafego <b>desta maquina</b> com o ' +
      '<code>dumpcap</code> e resume com o <code>tshark</code>: quem falou com quem, nomes consultados no DNS e ' +
      'sites acessados. As capturas ficam em <code>~/Capturas</code>.</p>' +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-capturar="10">⏺ 10 s</button>' +
      '<button class="xp-btn" data-dohsec-capturar="30">⏺ 30 s</button>' +
      '<button class="xp-btn" data-dohsec-capturar="60">⏺ 60 s</button>' +
      '<label class="dohsec-check-label"><input type="checkbox" id="dohsecCapExemplo" checked> gerar trafego de exemplo ' +
      '(acessa alguns sites durante a captura)</label></div>' +
      '<div id="dohsecCapOut"></div>' +
      '<h4>Suas capturas</h4>' + lista(d.capturas, 'Nenhuma ainda. Clique em um dos botoes acima.') +
      '<h4>Capturas dos casos do laboratorio</h4>' + lista(d.laboratorio, 'Inicie um caso com captura (ex.: Vazamento por DNS).'),
      { w: 'min(860px,94vw)', h: 'min(700px,86vh)' });
  }

  async function capturar(segundos) {
    const out = document.getElementById('dohsecCapOut');
    const exemplo = (document.getElementById('dohsecCapExemplo') || {}).checked;
    let resta = Number(segundos);
    out.innerHTML = '<div class="dohsec-gravando">⏺ Gravando... <b id="dohsecCapResta">' + resta + '</b> s</div>';
    const relogio = setInterval(() => {
      resta = Math.max(0, resta - 1);
      const el = document.getElementById('dohsecCapResta');
      if (el) el.textContent = resta;
    }, 1000);
    try {
      const r = await api('/api/captura', { segundos: Number(segundos), exemplo: !!exemplo });
      clearInterval(relogio);
      if (r.erro) { out.innerHTML = '<p class="dohsec-dica">' + esc(r.erro) + '</p>'; return; }
      await captura();
      mostraResumo(r);
    } catch (e) { clearInterval(relogio); out.innerHTML = '<p class="dohsec-dica">' + esc(e.message) + '</p>'; }
  }

  async function analisaCaptura(caminho) {
    const out = document.getElementById('dohsecCapOut');
    if (out) out.innerHTML = '<p class="dohsec-dica">Analisando...</p>';
    const r = await api('/api/captura/analisar?caminho=' + encodeURIComponent(caminho));
    if (r.erro) return aviso('Captura', r.erro);
    mostraResumo(r);
  }

  function mostraResumo(r) {
    const out = document.getElementById('dohsecCapOut');
    if (!out) return;
    const tabela = (titulo, itens) => '<h4>' + titulo + '</h4>' + (itens.length
      ? '<table class="dohsec-tabela"><tbody>' + itens.map(([v, n]) => '<tr><td class="dohsec-mono">' + esc(v) +
        '</td><td>' + n + 'x</td></tr>').join('') + '</tbody></table>'
      : '<p class="muted-mini">Nada nesta captura.</p>');
    out.innerHTML = '<div class="os-good"><b>📊 ' + esc(r.nome) + '</b>: ' + esc(r.pacotes) + ' pacotes. ' +
      '<button class="xp-btn dohsec-mini" data-dohsec-wireshark="' + esc(r.arquivo) + '">🦈 Abrir no Wireshark</button></div>' +
      '<h4>Quem falou com quem</h4>' + (r.conversas.length
        ? '<table class="dohsec-tabela"><thead><tr><th>De</th><th>Para</th><th>Pacotes</th><th>Bytes</th></tr></thead><tbody>' +
          r.conversas.map(c => '<tr><td class="dohsec-mono">' + esc(c.a) + '</td><td class="dohsec-mono">' + esc(c.b) +
            '</td><td>' + esc(c.quadros) + '</td><td>' + esc(c.bytes) + '</td></tr>').join('') + '</tbody></table>'
        : '<p class="muted-mini">Nenhuma conversa IP.</p>') +
      tabela('Nomes consultados no DNS', r.dns) +
      tabela('Sites acessados por HTTPS (SNI)', r.https) +
      tabela('Pedidos HTTP (sem criptografia)', r.http) +
      '<h4>Protocolos</h4>' + pre(r.protocolos);
  }

  async function abreWireshark(caminho) {
    const r = await api('/api/abrir', { programa: 'wireshark', arquivo: caminho });
    aviso(r.ok ? 'Abrindo o Wireshark' : 'Nao deu', r.ok ? caminho.split('/').pop() : r.erro);
  }

  // ---------------------------------------------------------------- Relatorio de Incidente
  // Diario do analista por caso + campos do relatorio; exporta Markdown e HTML para ~/Relatorios
  async function relatorios() {
    const d = await api('/api/relatorios');
    janela('reports', 'Relatórios de Incidente', '📝',
      '<h3>📝 Relatórios de Incidente</h3><p class="dohsec-dica">Cada caso tem um diário do analista e um ' +
      'relatório com linha do tempo, IOCs, evidências (com SHA-256) e remediação, igual ao da vida real. ' +
      'No Terminal: <code>relatorio anota "o que descobri"</code> dentro da pasta do caso.</p>' +
      (d.relatorios.length ? d.relatorios.map(r =>
        '<div class="dohsec-caso' + (r.resolvido ? ' dohsec-ok' : '') + '"><b>' + (r.resolvido ? '✅' : '🔎') + ' ' +
        r.n + '. ' + esc(r.titulo) + '</b> <span class="muted-mini">' + r.preenchidos + '/' + r.total_campos +
        ' campos, ' + r.anotacoes + ' anotações' + (r.atualizado ? ', ' + esc(r.atualizado) : '') + '</span>' +
        '<div class="dohsec-barra"><button class="xp-btn dohsec-mini" data-dohsec-relatorio="' + r.n +
        '">Abrir</button></div></div>').join('')
        : '<p class="muted-mini">Nenhum ainda. Investigue um caso na Mesa do Incidente e clique em 📝 Relatório.</p>') +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-dir="~/Relatorios">🗂️ Pasta ~/Relatorios</button>' +
      '<button class="xp-btn" data-dohsec-app="case">🚨 Mesa do Incidente</button></div>',
      { w: 'min(760px,94vw)', h: 'min(640px,82vh)' });
  }

  function diario(itens) {
    return itens.length ? itens.map(a => '<div class="dohsec-nota-diario"><span class="dohsec-mono">' + esc(a.quando) +
      '</span> ' + esc(a.texto) + '</div>').join('') : '<p class="muted-mini">Sem anotações. Anote cada pista que achar.</p>';
  }

  async function relatorio(n) {
    const d = await api('/api/relatorio?n=' + encodeURIComponent(n));
    if (d.bloqueado) return aviso('🔒 Ainda nao', d.erro);
    janela('relatorio_' + n, 'Relatório: ' + d.titulo, '📝',
      '<h3>📝 Relatório de Incidente: ' + esc(d.titulo) + '</h3>' +
      '<p class="dohsec-dica">Preencha enquanto investiga. Caso, analista, situação e a lista de evidências ' +
      'com SHA-256 entram sozinhos.</p>' +
      '<h4>Diário do analista</h4><div id="dohsecDiario_' + n + '">' + diario(d.dados.diario) + '</div>' +
      '<div class="cli-row"><input id="dohsecAnota_' + n + '" maxlength="1000" placeholder="ex.: 14:02 achei 312 falhas de login vindas de 203.0.113.7">' +
      '<button class="xp-btn" data-dohsec-anotar="' + n + '">Anotar</button></div>' +
      d.campos.map(c => '<h4>' + esc(c.nome) + '</h4><div class="muted-mini">' + esc(c.ajuda) + '</div>' +
        '<textarea class="dohsec-campo" id="dohsecRel_' + n + '_' + c.chave + '" rows="' +
        (c.chave === 'resumo' || c.chave === 'impacto' || c.chave === 'licoes' ? 3 : 5) + '">' +
        esc(d.dados.campos[c.chave] || '') + '</textarea>').join('') +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-relsalvar="' + n + '">💾 Salvar</button>' +
      '<button class="xp-btn" data-dohsec-relver="' + n + '">👁️ Ver relatório</button>' +
      '<button class="xp-btn" data-dohsec-relexportar="' + n + '">📤 Exportar para ~/Relatorios</button></div>' +
      '<div id="dohsecRelOut_' + n + '"></div>',
      { w: 'min(860px,94vw)', h: 'min(700px,86vh)' });
    relatorioCampos[n] = d.campos.map(c => c.chave);
  }
  const relatorioCampos = {};

  async function salvaRelatorio(n, quieto) {
    const campos = {};
    (relatorioCampos[n] || []).forEach(k => {
      const el = document.getElementById('dohsecRel_' + n + '_' + k);
      if (el) campos[k] = el.value;
    });
    const r = await api('/api/relatorio/salvar', { n: Number(n), campos });
    if (r.bloqueado) throw new Error(r.erro);
    if (!quieto) aviso('Relatório salvo', 'Caso ' + n + ', ' + r.atualizado);
    if (existe('reports')) {
      // Atualiza a lista sem tirar o relatorio da frente
      await relatorios();
      if (existe('relatorio_' + n)) OS.focusWin(existe('relatorio_' + n));
    }
  }

  async function anotaRelatorio(n) {
    const campo = document.getElementById('dohsecAnota_' + n);
    const texto = campo ? campo.value.trim() : '';
    if (!texto) return aviso('Diário', 'Escreva a anotação primeiro.');
    const r = await api('/api/relatorio/anotar', { n: Number(n), texto });
    if (!r.ok) return aviso('Diário', r.erro);
    campo.value = '';
    const alvo = document.getElementById('dohsecDiario_' + n);
    if (alvo) alvo.innerHTML = diario(r.diario);
  }

  async function verRelatorio(n) {
    await salvaRelatorio(n, true);
    const d = await api('/api/relatorio?n=' + encodeURIComponent(n));
    janela('relatorio_ver_' + n, 'Relatório (prévia)', '👁️',
      '<div class="dohsec-relatorio">' + markdown(d.markdown) + '</div>' +
      '<div class="dohsec-barra"><button class="xp-btn" data-dohsec-relexportar="' + n + '">📤 Exportar para ~/Relatorios</button></div>',
      { w: 'min(900px,94vw)', h: 'min(720px,86vh)' });
  }

  async function exportaRelatorio(n) {
    if (existe('relatorio_' + n)) await salvaRelatorio(n, true);
    const r = await api('/api/relatorio/exportar', { n: Number(n) });
    if (!r.ok) return aviso('Nao deu', r.erro);
    aviso('Relatório exportado', r.html.split('/').pop());
    const out = document.getElementById('dohsecRelOut_' + n);
    if (out) out.innerHTML = '<div class="os-good"><b>📤 Exportado:</b><br><code>' + esc(r.md) + '</code><br><code>' +
      esc(r.html) + '</code> (abra no navegador para imprimir ou salvar em PDF)<div class="dohsec-barra">' +
      '<button class="xp-btn dohsec-mini" data-dohsec-dir="~/Relatorios">🗂️ Abrir a pasta</button></div></div>';
  }

  // ---------------------------------------------------------------- Conquistas
  // Medalhas conferidas de verdade (historico do bash, casos, relatorios, capturas, apps)
  function faixaMedalhas(m) {
    if (!m) return '';
    const ganhas = m.conquistas.filter(x => x.ganha);
    return '<h4>Conquistas <span class="muted-mini">' + m.ganhas + '/' + m.total + '</span></h4>' +
      '<div class="dohsec-faixa">' + (ganhas.length
        ? ganhas.map(x => '<span title="' + esc(x.nome + ': ' + x.descricao) + '">' + esc(x.icone) + '</span>').join('')
        : '<span class="muted-mini">Nenhuma ainda. Use o Terminal e resolva casos para ganhar medalhas.</span>') +
      ' <button class="xp-btn dohsec-mini" data-dohsec-app="medals">🏅 Ver todas</button></div>';
  }

  async function medalhas() {
    const m = await api('/api/conquistas?avisar=1');
    const grupos = [...new Set(m.conquistas.map(x => x.grupo))];
    janela('medals', 'Conquistas', '🏅',
      '<h3>🏅 Conquistas <span class="muted-mini">' + m.ganhas + ' de ' + m.total + '</span></h3>' +
      barra(m.ganhas, m.total) +
      '<p class="dohsec-dica">Tudo conferido de verdade: comandos que você usou no Terminal, casos resolvidos, ' +
      'relatórios, capturas e os apps. Medalha ganha não se perde. No Terminal: <code>conquistas</code>.</p>' +
      grupos.map(g => '<h4>' + esc(g) + '</h4><div class="dohsec-medalhas">' +
        m.conquistas.filter(x => x.grupo === g).map(x =>
          '<div class="dohsec-medalha' + (x.ganha ? '' : ' dohsec-trancado') + '">' +
          '<span class="dohsec-medalha-icone">' + (x.ganha ? esc(x.icone) : '🔒') + '</span>' +
          '<b>' + esc(x.nome) + '</b><span class="muted-mini">' +
          (x.ganha ? esc(x.descricao) + '<br>' + esc(x.data) : esc(x.como)) + '</span></div>').join('') +
        '</div>').join(''),
      { w: 'min(860px,94vw)', h: 'min(700px,86vh)' });
  }

  // Avisa na tela cada medalha nova (uma vez so)
  let conferindo = false;
  async function confereConquistas() {
    if (conferindo || !document.getElementById('wins')) return;
    conferindo = true;
    try {
      const m = await api('/api/conquistas?avisar=1');
      m.novas.forEach((x, i) => setTimeout(() => {
        som('conquista');
        aviso('🏅 Conquista desbloqueada!', x.icone + ' ' + x.nome);
      }, i * 1500));
    } catch (e) { /* tenta de novo no proximo ciclo */ } finally { conferindo = false; }
  }

  // ---------------------------------------------------------------- Janelas como num SO de verdade
  // Janelas de fora do front (Wireshark, terminal do Ctrl+Alt+T) ganham botao na barra de tarefas:
  // clicar traz para a frente, clicar de novo na ativa minimiza.
  let janelaDeForaAtiva = false;
  async function sincronizaJanelas() {
    const barraTarefas = document.getElementById('tasks');
    if (!barraTarefas) return;
    let d;
    try { d = await api('/api/janelas'); } catch (e) { return; }
    janelaDeForaAtiva = d.janelas.some(j => j.ativa);
    const vistos = new Set();
    d.janelas.forEach(j => {
      const id = 'xwin_' + j.id;
      vistos.add(id);
      let b = document.getElementById(id);
      if (!b) {
        b = document.createElement('button');
        b.id = id;
        b.className = 'task-btn dohsec-xwin';
        b.setAttribute('data-dohsec-xwin', j.id);
        barraTarefas.appendChild(b);
      }
      const texto = j.icone + ' ' + j.titulo;
      if (b.textContent !== texto) b.textContent = texto;
      b.title = j.titulo;
      b.classList.toggle('active', j.ativa);
      b.classList.toggle('dohsec-oculta', j.oculta);
    });
    barraTarefas.querySelectorAll('.dohsec-xwin').forEach(b => { if (!vistos.has(b.id)) b.remove(); });
  }

  async function alternaJanela(wid) {
    // O clique na barra ja tira o foco da janela; vale o estado de antes do clique
    const b = document.getElementById('xwin_' + wid);
    const minimizar = !!b && b.classList.contains('active') && !b.classList.contains('dohsec-oculta');
    await api('/api/janelas/alternar', { id: wid, minimizar });
    setTimeout(sincronizaJanelas, 300);
  }

  // Botao da tarefa do front: se a janela ja esta na frente, minimiza (o esboco so trazia para a frente)
  window.addEventListener('pointerdown', e => {
    const b = e.target.closest && e.target.closest('.task-btn');
    if (!b || !b.id.startsWith('task_') || janelaDeForaAtiva) return;
    const w = document.getElementById('win_' + b.id.slice(5));
    if (w && w.classList.contains('active-window') && w.style.display !== 'none') {
      e.preventDefault();
      e.stopPropagation();
      w.style.display = 'none';
      w.classList.remove('active-window');
      b.classList.remove('active');
    }
  }, true);

  // Duplo clique na barra de titulo maximiza e restaura
  document.addEventListener('dblclick', e => {
    const barra = e.target.closest && e.target.closest('#wins .titlebar');
    if (!barra || e.target.closest('.win-btn')) return;
    const w = barra.closest('.window');
    w.classList.toggle('maximized');
    OS.focusWin(w);
  }, true);

  // ---------------------------------------------------------------- Energia
  async function energia(acao) {
    const frase = acao === 'desligar' ? 'Desligar o D\'OH!Sec OS?' : 'Reiniciar o D\'OH!Sec OS?';
    if (!(await confirma(frase))) return;
    try {
      const r = await api('/api/energia', { acao });
      if (r.ok) aviso(acao === 'desligar' ? 'Desligando' : 'Reiniciando', 'Ate ja!');
      else aviso('Nao deu para ' + acao, r.erro);
    } catch (e) { aviso('Erro', e.message); }
  }

  function menuEnergia() {
    const pop = document.querySelector('#startmenu .os-menu-pop');
    if (!pop || pop.querySelector('.dohsec-energia')) return;
    const div = document.createElement('div');
    div.className = 'dohsec-energia';
    div.innerHTML = '<button class="sm-item" data-dohsec-energia="reiniciar">🔄 Reiniciar</button>' +
      '<button class="sm-item" data-dohsec-energia="desligar">🔌 Desligar</button>';
    pop.appendChild(div);
  }

  // ---------------------------------------------------------------- registro
  window.DOHSEC_REAL = {
    terminal: terminal,
    processes: processos,
    network: rede,
    logs: () => logs('sistema'),
    siem: siem,
    permissions: permissoes,
    updates: updates,
    files: () => arquivos(''),
    lab: laboratorio,
    goals: minhaCarreira,
    case: mesa,
    certificate: certificado,
    tools: ferramentas,
    burns: painelBurns,
    inspector: () => inspetor(''),
    capture: captura,
    reports: relatorios,
    medals: medalhas,
  };

  // Apps novos no desktop e no menu Iniciar (o front monta os icones no login)
  [['files', 'Arquivos', '🗂️'], ['tools', 'Ferramentas', '🧰'], ['burns', 'Painel do Sr. Burns', '👔'],
    ['inspector', 'Inspetor de Arquivos', '🔬'],
    ['capture', 'Captura de Rede', '🦈'],
    ['reports', 'Relatórios', '📝'],
    ['medals', 'Conquistas', '🏅'],
    ['lab', 'Laboratório', '🧪']].forEach(a => {
    if (!OS.apps.find(x => x[0] === a[0])) OS.apps.splice(2, 0, a);
  });
  const objetivos = OS.apps.find(x => x[0] === 'goals');
  if (objetivos) objetivos[1] = 'Minha carreira';
  const menu = document.getElementById('startmenu');
  if (menu) new MutationObserver(() => { menuEnergia(); pintaCargo(); }).observe(menu, { childList: true, subtree: true });
  const wins = document.getElementById('wins');
  if (wins) new MutationObserver(pintaCargo).observe(wins, { childList: true });
  relogio();
  setInterval(relogio, 20000);
  setInterval(confereConquistas, 15000);
  setInterval(sincronizaJanelas, 2000);
  login();

  // Cliques dos apps reais (em fase de captura, como o front faz)
  const acoes = [
    ['data-dohsec-kill', v => encerra(v)],
    ['data-dohsec-app', v => window.DOHSEC_REAL[v] && window.DOHSEC_REAL[v]()],
    ['data-dohsec-logs', v => logs(v)],
    ['data-dohsec-siem', () => buscaSiem()],
    ['data-dohsec-update', () => abreTerminal('terminal_update', 'Updates no Terminal', '', 'atualizar')],
    ['data-dohsec-dir', v => arquivos(v === '~' ? '' : v.replace(/^~/, '/home/' + (document.body.dataset.u || '')))],
    ['data-dohsec-ver', v => verArquivo(v)],
    ['data-dohsec-ocultos', () => { mostraOcultos = !mostraOcultos; arquivos(pastaAtual); }],
    ['data-dohsec-termaqui', v => abreTerminal('terminal_' + Date.now(), 'Terminal', v, '')],
    ['data-dohsec-caso', v => abreCaso(v)],
    ['data-dohsec-investigar', v => abreTerminal('terminal_' + v.split('/').pop(), 'Investigação', v, '')],
    ['data-dohsec-dica', v => dica(v)],
    ['data-dohsec-responder', v => responder(v)],
    ['data-dohsec-energia', v => energia(v)],
    ['data-dohsec-abrir', v => abrePrograma(v)],
    ['data-dohsec-salvar-cert', () => salvaCertificado()],
    ['data-dohsec-nome', v => gravaNome(v)],
    ['data-dohsec-corrigir', v => corrigeBurns(v)],
    ['data-dohsec-inspecionar', v => inspeciona(v)],
    ['data-dohsec-capturar', v => capturar(v)],
    ['data-dohsec-analisar', v => analisaCaptura(v)],
    ['data-dohsec-wireshark', v => abreWireshark(v)],
    ['data-dohsec-relatorio', v => relatorio(v)],
    ['data-dohsec-anotar', v => anotaRelatorio(v)],
    ['data-dohsec-relsalvar', v => salvaRelatorio(v)],
    ['data-dohsec-relver', v => verRelatorio(v)],
    ['data-dohsec-relexportar', v => exportaRelatorio(v)],
    ['data-dohsec-xwin', v => alternaJanela(v)],
    ['data-dohsec-resposta', v => { if (respostaPendente) respostaPendente(v === 'sim'); }],
  ];
  document.addEventListener('click', e => {
    for (const [attr, fn] of acoes) {
      const el = e.target.closest('[' + attr + ']');
      if (el) {
        e.preventDefault();
        e.stopPropagation();
        Promise.resolve(fn(el.getAttribute(attr))).catch(err => aviso('Erro', err.message))
          .then(() => setTimeout(confereConquistas, 800));
        return;
      }
    }
  }, true);
  // Na janela (antes do documento): o nome precisa sair antes de o front abrir a carreira
  window.addEventListener('pointerdown', e => {
    if (e.target.closest && e.target.closest('#enter')) nomePendente = salvaNome();
  }, true);
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter' || !e.target || !e.target.id) return;
    if (e.target.id === 'dohsecSiemQ') { e.preventDefault(); buscaSiem(); }
    if (e.target.id === 'dohsecInspQ') { e.preventDefault(); inspeciona('campo'); }
    const nomeCampo = e.target.id.match(/^dohsecNome_(\w+)$/);
    if (nomeCampo) { e.preventDefault(); gravaNome(nomeCampo[1]); }
    const nota = e.target.id.match(/^dohsecAnota_(\d+)$/);
    if (nota) { e.preventDefault(); anotaRelatorio(nota[1]); }
    const m = e.target.id.match(/^dohsecResp_(\d+)$/);
    if (m) { e.preventDefault(); responder(m[1]); }
  }, true);

  // Nome do usuario (para os atalhos ~ do gerenciador de arquivos)
  api('/api/sistema').then(s => {
    document.body.dataset.u = s.usuario;
    // ISO live sem persistencia: avisa uma vez, ao entrar no desktop, que o progresso nao fica salvo
    if (s.live && !s.persistente) {
      const avisaPersistencia = () => setTimeout(() => aviso('⚠️ Progresso nao sera salvo',
        'Esta ISO roda da memoria. Para guardar: adicione um disco vazio a VM e rode sudo dohsec-persistencia'), 2500);
      // Na janela, em captura: o front para o clique do botao Entrar antes de ele chegar ao botao
      if (document.getElementById('enter')) {
        const aoEntrar = e => {
          if (!e.target.closest || !e.target.closest('#enter')) return;
          window.removeEventListener('pointerdown', aoEntrar, true);
          avisaPersistencia();
        };
        window.addEventListener('pointerdown', aoEntrar, true);
      } else {
        avisaPersistencia();
      }
    }
  }).catch(() => {});
})();

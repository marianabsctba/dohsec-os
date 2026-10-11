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
      pre(d.pendentes) +
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
      '</div><table class="dohsec-tabela"><thead><tr><th>Nome</th><th>Tamanho</th><th>Permissão</th></tr></thead><tbody>' +
      itens.map(i => '<tr class="dohsec-linha" data-dohsec-' + (i.pasta ? 'dir' : 'ver') + '="' +
        esc(d.caminho.replace(/\/$/, '') + '/' + i.nome) + '"><td>' + (i.pasta ? '📁 ' : '📄 ') + esc(i.nome) +
        '</td><td>' + (i.pasta ? '' : tamanho(i.tamanho)) + '</td><td class="dohsec-mono">' + i.modo +
        '</td></tr>').join('') + '</tbody></table>');
  }

  async function verArquivo(caminho) {
    const d = await api('/api/arquivo?caminho=' + encodeURIComponent(caminho));
    if (d.erro) return aviso('Arquivos', d.erro);
    janela('viewer', d.caminho.split('/').pop(), '📄',
      '<h3>📄 ' + esc(d.caminho) + '</h3>' +
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
      '<button class="xp-btn" data-dohsec-app="tools">🧰 Ferramentas</button></div>' +
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
    if (!r.certo) return aviso("D'oh!", 'Nao e isso. Tente de novo ou peca uma dica.');
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
    g.fillText(k.feitos + ' de ' + k.total + ' casos resolvidos com ferramentas reais do Debian', 600, 600);
    const ultima = k.promocoes.length ? k.promocoes[k.promocoes.length - 1].data : new Date().toISOString().slice(0, 10);
    g.fillText('Emitido em ' + ultima + '  -  Ass.: C. M. Burns (por W. Smithers)', 600, 680);
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
      ['tcpdump', 'capturar trafego'], ['yara', 'regras de deteccao'], ['awk', 'colunas de logs']]],
    ['Chefe de Seguranca', [['exiftool', 'metadados'], ['binwalk', 'arquivos dentro de arquivos'], ['sleuthkit (fls, icat)', 'forense de disco'],
      ['foremost', 'recuperar arquivos'], ['aide', 'integridade'], ['ufw / nft', 'firewall'], ['ausearch', 'auditoria (auditd)'],
      ['lynis', 'auditoria de endurecimento'], ['suricata', 'IDS']]],
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

  // ---------------------------------------------------------------- Energia
  async function energia(acao) {
    const frase = acao === 'desligar' ? 'Desligar o D\'OH!Sec OS?' : 'Reiniciar o D\'OH!Sec OS?';
    if (!window.confirm(frase)) return;
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
  };

  // Apps novos no desktop e no menu Iniciar (o front monta os icones no login)
  [['files', 'Arquivos', '🗂️'], ['tools', 'Ferramentas', '🧰'], ['lab', 'Laboratório', '🧪']].forEach(a => {
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
  ];
  document.addEventListener('click', e => {
    for (const [attr, fn] of acoes) {
      const el = e.target.closest('[' + attr + ']');
      if (el) {
        e.preventDefault();
        e.stopPropagation();
        Promise.resolve(fn(el.getAttribute(attr))).catch(err => aviso('Erro', err.message));
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
    const nomeCampo = e.target.id.match(/^dohsecNome_(\w+)$/);
    if (nomeCampo) { e.preventDefault(); gravaNome(nomeCampo[1]); }
    const m = e.target.id.match(/^dohsecResp_(\d+)$/);
    if (m) { e.preventDefault(); responder(m[1]); }
  }, true);

  // Nome do usuario (para os atalhos ~ do gerenciador de arquivos)
  api('/api/sistema').then(s => { document.body.dataset.u = s.usuario; }).catch(() => {});
})();

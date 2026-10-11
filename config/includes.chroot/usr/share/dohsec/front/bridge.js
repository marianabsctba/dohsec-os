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

  // ---------------------------------------------------------------- Laboratorio
  async function laboratorio() {
    const d = await api('/api/lab');
    const feitos = d.casos.filter(c => c.resolvido).length;
    let html = '<h3>🧪 Laboratório Springfield</h3><p class="dohsec-dica">' + feitos + '/' + d.casos.length +
      ' concluídos. Comece pela Trilha do Estagiário e vá subindo. Tudo aqui é real: as evidências ' +
      'ficam em <code>~/springfield/casos</code> e você investiga no Terminal.</p>';
    d.trilhas.forEach(t => {
      const itens = d.casos.filter(c => c.trilha === t.id);
      if (!itens.length) return;
      html += '<h4>' + esc(t.nome) + ' <span class="muted-mini">' + esc(t.sub) + ' (' +
        itens.filter(c => c.resolvido).length + '/' + itens.length + ')</span></h4>';
      html += itens.map(c => '<div class="dohsec-caso' + (c.resolvido ? ' dohsec-ok' : '') + '">' +
        '<b>' + c.n + '. ' + esc(c.titulo) + '</b> <span class="muted-mini">' + esc(c.nivel) + '</span> ' +
        (c.resolvido ? '✅' : (c.iniciado ? '🔎' : '')) +
        '<div class="dohsec-barra"><button class="xp-btn dohsec-mini" data-dohsec-caso="' + c.n + '">Abrir</button></div></div>'
      ).join('');
    });
    janela('lab', 'Laboratório', '🧪', html, { w: 'min(760px,94vw)', h: 'min(640px,82vh)' });
  }

  async function abreCaso(n) {
    const r = await api('/api/lab/iniciar', { n: Number(n) });
    const d = await api('/api/lab');
    const c = d.casos.find(x => x.n === Number(n));
    janela('caso_' + n, c.titulo, '🔎',
      '<div class="dohsec-barra">' +
      '<button class="xp-btn" data-dohsec-investigar="' + esc(r.pasta) + '">💻 Investigar no Terminal</button> ' +
      '<button class="xp-btn" data-dohsec-dir="' + esc(r.pasta) + '">🗂️ Ver arquivos</button></div>' +
      pre(r.leiame.replace(/`/g, '')) +
      '<h4>Sua resposta</h4><div class="cli-row"><input id="dohsecResp_' + n + '" placeholder="digite a resposta">' +
      '<button class="xp-btn" data-dohsec-responder="' + n + '">Responder</button>' +
      '<button class="xp-btn" data-dohsec-dica="' + n + '">Dica</button></div>' +
      '<div id="dohsecCasoOut_' + n + '">' +
      (c.dicas.length ? '<p class="dohsec-dica">💡 ' + c.dicas.map(esc).join('<br>💡 ') + '</p>' : '') +
      (c.resolvido ? aprendizado(c.aprendizado) : '') + '</div>',
      { w: 'min(860px,94vw)', h: 'min(680px,84vh)' });
  }

  function aprendizado(itens) {
    return '<div class="os-good"><b>✅ Resolvido! O que aprendemos</b><ul>' +
      itens.map(i => '<li>' + esc(i) + '</li>').join('') + '</ul></div>';
  }

  async function dica(n) {
    const d = await api('/api/lab/dica', { n: Number(n) });
    const out = document.getElementById('dohsecCasoOut_' + n);
    if (out) out.innerHTML = '<p class="dohsec-dica">💡 ' + d.dicas.map(esc).join('<br>💡 ') + '</p>';
  }

  async function responder(n) {
    const campo = document.getElementById('dohsecResp_' + n);
    const r = await api('/api/lab/responder', { n: Number(n), resposta: campo ? campo.value : '' });
    const out = document.getElementById('dohsecCasoOut_' + n);
    if (r.certo) {
      aviso('Mmm... resolvido!', 'Caso ' + n + ' concluído');
      if (out) out.innerHTML = aprendizado(r.aprendizado);
      if (existe('lab')) laboratorio();
    } else {
      aviso("D'oh!", 'Não é isso. Tente de novo ou peça uma dica.');
    }
  }

  // ---------------------------------------------------------------- Energia
  async function energia(acao) {
    const frase = acao === 'desligar' ? 'Desligar o D\'OH!Sec OS?' : 'Reiniciar o D\'OH!Sec OS?';
    if (!window.confirm(frase)) return;
    try { await api('/api/energia', { acao }); } catch (e) { aviso('Erro', e.message); }
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
  };

  // Apps novos no desktop e no menu Iniciar (o front monta os icones no login)
  [['files', 'Arquivos', '🗂️'], ['lab', 'Laboratório', '🧪']].forEach(a => {
    if (!OS.apps.find(x => x[0] === a[0])) OS.apps.splice(2, 0, a);
  });
  const menu = document.getElementById('startmenu');
  if (menu) new MutationObserver(menuEnergia).observe(menu, { childList: true, subtree: true });

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
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter' || !e.target || !e.target.id) return;
    if (e.target.id === 'dohsecSiemQ') { e.preventDefault(); buscaSiem(); }
    const m = e.target.id.match(/^dohsecResp_(\d+)$/);
    if (m) { e.preventDefault(); responder(m[1]); }
  }, true);

  // Nome do usuario (para os atalhos ~ do gerenciador de arquivos)
  api('/api/sistema').then(s => { document.body.dataset.u = s.usuario; }).catch(() => {});
})();

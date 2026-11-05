// JavaScript do Visualizador do Compilador Procedural RPG
(function () {
  'use strict';

  const dadosScript = document.getElementById('dados-compilador');
  if (!dadosScript) return;

  const DADOS = JSON.parse(dadosScript.textContent);

  // Elementos DOM principais
  const headerArquivo = document.getElementById('header-arquivo-nome');
  const stepperFases = document.getElementById('stepper-fases');
  const codigoConteiner = document.getElementById('codigo-conteiner');
  const tabelaTokensCorpo = document.getElementById('tabela-tokens-corpo');
  const filtrosCategoria = document.getElementById('filtros-categoria');
  const buscaToken = document.getElementById('busca-token');
  const resumoTokens = document.getElementById('resumo-tokens');
  const chkMostrarLayout = document.getElementById('chk-mostrar-layout');

  let categoriaAtiva = 'todas';
  let termoBusca = '';

  // 1. Inicializa cabeçalho e Stepper
  function initHeader() {
    headerArquivo.textContent = DADOS.arquivo;

    stepperFases.innerHTML = '';
    DADOS.fases.forEach((fase, idx) => {
      const item = document.createElement('div');
      item.className = `stepper-item status-${fase.status}`;
      
      let iconeStatus = '✓';
      if (fase.status === 'erro') iconeStatus = '✗';
      if (fase.status === 'bloqueada') iconeStatus = '🔒';
      if (fase.status === 'pendente') iconeStatus = '⏳';

      item.innerHTML = `<span>${iconeStatus}</span> <span>${fase.nome}</span>`;
      item.title = fase.resumo;

      item.addEventListener('click', () => {
        const abaId = `aba-${fase.id}`;
        ativarAba(abaId);
      });

      stepperFases.appendChild(item);

      if (idx < DADOS.fases.length - 1) {
        const sep = document.createElement('span');
        sep.className = 'stepper-separador';
        sep.textContent = '─▶';
        stepperFases.appendChild(sep);
      }
    });
  }

  // 2. Renderiza o Código Fonte com spans e erros
  function renderizarCodigoFonte() {
    codigoConteiner.innerHTML = '';
    const linhas = DADOS.fonte.split('\n');
    const tokensPorLinha = {};

    DADOS.tokens.forEach(tok => {
      if (!tokensPorLinha[tok.linha]) tokensPorLinha[tok.linha] = [];
      tokensPorLinha[tok.linha].push(tok);
    });

    const errosPorLinha = {};
    DADOS.erros.forEach(err => {
      if (!errosPorLinha[err.linha]) errosPorLinha[err.linha] = [];
      errosPorLinha[err.linha].push(err);
    });

    linhas.forEach((conteudoLinha, idx) => {
      const numLinha = idx + 1;
      const linhaDiv = document.createElement('div');
      linhaDiv.className = 'codigo-linha';
      linhaDiv.id = `cod-linha-${numLinha}`;
      if (errosPorLinha[numLinha]) {
        linhaDiv.classList.add('linha-com-erro');
      }

      const numSpan = document.createElement('span');
      numSpan.className = 'linha-num';
      numSpan.textContent = numLinha;

      const conteudoSpan = document.createElement('span');
      conteudoSpan.className = 'linha-conteudo';

      const tokensDaLinha = (tokensPorLinha[numLinha] || []).filter(t => !t.sintetico);

      if (tokensDaLinha.length === 0) {
        // Linha sem tokens (vazia ou só comentário)
        const textoEscapado = conteudoLinha.trim().startsWith('//')
          ? `<span class="tok-comentario">${escapeHtml(conteudoLinha)}</span>`
          : escapeHtml(conteudoLinha);
        conteudoSpan.innerHTML = textoEscapado;
      } else {
        // Reconstrói linha fatiando com base nos tokens reais
        let htmlLinha = '';
        let cursor = 0;

        tokensDaLinha.forEach(tok => {
          const colIni = tok.coluna - 1;
          const colFim = tok.coluna_fim - 1;

          if (colIni > cursor) {
            const trechoAntes = conteudoLinha.slice(cursor, colIni);
            if (trechoAntes.includes('//')) {
              htmlLinha += `<span class="tok-comentario">${escapeHtml(trechoAntes)}</span>`;
            } else {
              htmlLinha += escapeHtml(trechoAntes);
            }
          }

          const textoToken = conteudoLinha.slice(colIni, colFim);
          htmlLinha += `<span class="tok-span tok-${tok.categoria}" data-token-id="${tok.i}" data-linha="${tok.linha}">${escapeHtml(textoToken || tok.texto)}</span>`;
          cursor = colFim;
        });

        if (cursor < conteudoLinha.length) {
          const sobra = conteudoLinha.slice(cursor);
          if (sobra.includes('//')) {
            htmlLinha += `<span class="tok-comentario">${escapeHtml(sobra)}</span>`;
          } else {
            htmlLinha += escapeHtml(sobra);
          }
        }
        conteudoSpan.innerHTML = htmlLinha;
      }

      linhaDiv.appendChild(numSpan);
      linhaDiv.appendChild(conteudoSpan);
      codigoConteiner.appendChild(linhaDiv);

      // Se houver erro nesta linha, insere o banner de diagnóstico
      if (errosPorLinha[numLinha]) {
        errosPorLinha[numLinha].forEach(erro => {
          const erroBanner = document.createElement('div');
          erroBanner.className = 'erro-inline-banner';
          const espacosSeta = ' '.repeat(Math.max(0, erro.coluna - 1));
          erroBanner.innerHTML = `
            <div style="font-family: var(--fonte-mono);"><span class="seta-apontador">▲</span></div>
            <div>
              <strong>[Erro ${erro.fase}] Coluna ${erro.coluna}:</strong> ${escapeHtml(erro.mensagem)}
            </div>
          `;
          codigoConteiner.appendChild(erroBanner);
        });
      }
    });

    // Eventos de hover nos spans de código
    codigoConteiner.addEventListener('mouseover', e => {
      const span = e.target.closest('.tok-span');
      if (span) {
        const tokenId = span.dataset.tokenId;
        destacarToken(tokenId);
      }
    });

    codigoConteiner.addEventListener('mouseout', e => {
      const span = e.target.closest('.tok-span');
      if (span) {
        removerDestaqueToken();
      }
    });
  }

  // 3. Aba Léxica: Tabela de Tokens e Filtros
  function initAbaLexica() {
    const categorias = {};
    DADOS.tokens.forEach(t => {
      categorias[t.categoria] = (categorias[t.categoria] || 0) + 1;
    });

    filtrosCategoria.innerHTML = `
      <button class="filtro-chip ativo" data-cat="todas">Todos (${DADOS.tokens.length})</button>
    `;
    Object.keys(categorias).sort().forEach(cat => {
      const chip = document.createElement('button');
      chip.className = 'filtro-chip';
      chip.dataset.cat = cat;
      chip.textContent = `${cat} (${categorias[cat]})`;
      chip.addEventListener('click', () => {
        document.querySelectorAll('.filtro-chip').forEach(c => c.classList.remove('ativo'));
        chip.classList.add('ativo');
        categoriaAtiva = cat;
        renderizarTabelaTokens();
      });
      filtrosCategoria.appendChild(chip);
    });

    filtrosCategoria.querySelector('[data-cat="todas"]').addEventListener('click', e => {
      document.querySelectorAll('.filtro-chip').forEach(c => c.classList.remove('ativo'));
      e.target.classList.add('ativo');
      categoriaAtiva = 'todas';
      renderizarTabelaTokens();
    });

    buscaToken.addEventListener('input', e => {
      termoBusca = e.target.value.toLowerCase().trim();
      renderizarTabelaTokens();
    });

    renderizarTabelaTokens();
  }

  function renderizarTabelaTokens() {
    tabelaTokensCorpo.innerHTML = '';
    const tokensFiltrados = DADOS.tokens.filter(tok => {
      if (!chkMostrarLayout.checked && tok.sintetico) return false;
      if (categoriaAtiva !== 'todas' && tok.categoria !== categoriaAtiva) return false;
      if (termoBusca) {
        const matchTipo = tok.tipo.toLowerCase().includes(termoBusca);
        const matchTexto = (tok.texto || '').toLowerCase().includes(termoBusca);
        if (!matchTipo && !matchTexto) return false;
      }
      return true;
    });

    resumoTokens.textContent = `Exibindo ${tokensFiltrados.length} de ${DADOS.tokens.length} tokens`;

    tokensFiltrados.forEach(tok => {
      const tr = document.createElement('tr');
      tr.id = `tab-token-${tok.i}`;
      tr.innerHTML = `
        <td style="color: var(--texto-fraco);">${tok.i}</td>
        <td><strong>${escapeHtml(tok.tipo)}</strong></td>
        <td><code>${escapeHtml(JSON.stringify(tok.texto))}</code></td>
        <td>${tok.linha}</td>
        <td>${tok.coluna}</td>
        <td><span class="badge-cat tok-${tok.categoria}">${tok.categoria}</span></td>
      `;

      tr.addEventListener('mouseenter', () => {
        destacarToken(tok.i);
        scrollParaLinha(tok.linha);
      });

      tr.addEventListener('mouseleave', () => {
        removerDestaqueToken();
      });

      tabelaTokensCorpo.appendChild(tr);
    });
  }

  // Funções de realce bidirecional
  function destacarToken(tokenId) {
    removerDestaqueToken();
    const span = document.querySelector(`.tok-span[data-token-id="${tokenId}"]`);
    if (span) span.classList.add('destaque-token');

    const tr = document.getElementById(`tab-token-${tokenId}`);
    if (tr) {
      tr.style.backgroundColor = 'var(--bg-hover)';
      tr.style.outline = '1px solid var(--cor-primaria)';
    }

    if (span) {
      const linha = span.dataset.linha;
      const linhaDiv = document.getElementById(`cod-linha-${linha}`);
      if (linhaDiv) linhaDiv.classList.add('destaque-linha');
    }
  }

  function removerDestaqueToken() {
    document.querySelectorAll('.tok-span.destaque-token').forEach(s => s.classList.remove('destaque-token'));
    document.querySelectorAll('.codigo-linha.destaque-linha').forEach(l => l.classList.remove('destaque-linha'));
    document.querySelectorAll('.tabela-tokens tr').forEach(tr => {
      tr.style.backgroundColor = '';
      tr.style.outline = '';
    });
  }

  function scrollParaLinha(numLinha) {
    const el = document.getElementById(`cod-linha-${numLinha}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function ativarAba(abaId) {
    document.querySelectorAll('.aba-btn').forEach(btn => {
      if (btn.dataset.aba === abaId) btn.classList.add('ativa');
      else btn.classList.remove('ativa');
    });

    document.querySelectorAll('.aba-conteudo').forEach(cont => {
      if (cont.id === abaId) cont.classList.add('ativa');
      else cont.classList.remove('ativa');
    });
  }

  function escapeHtml(texto) {
    if (!texto) return '';
    return String(texto)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // 4. Aba Sintática: Árvore Expansível e Diagrama
  const btnVisaoArvore = document.getElementById('btn-visao-arvore');
  const btnVisaoDiagrama = document.getElementById('btn-visao-diagrama');
  const btnExpandirTudo = document.getElementById('btn-expandir-tudo');
  const btnRecolherTudo = document.getElementById('btn-recolher-tudo');
  const chkModoCompacto = document.getElementById('chk-modo-compacto');
  const arvoreConteiner = document.getElementById('arvore-conteiner');
  const diagramaConteiner = document.getElementById('diagrama-conteiner');
  const sintaticoInfo = document.getElementById('sintatico-info');

  let noSelecionado = null;

  function initAbaSintatica() {
    if (!DADOS.arvore) {
      arvoreConteiner.innerHTML = `
        <div class="narrativa-aviso" style="border-left-color: var(--cor-aviso); color: #fde68a; background: rgba(245, 158, 11, 0.1);">
          <span>🔒 <strong>Árvore Sintática não gerada:</strong> O pipeline foi interrompido na fase léxica para evitar erros em cascata falsos. Corrija os erros léxicos no código para gerar a árvore.</span>
        </div>
      `;
      return;
    }

    btnVisaoArvore.addEventListener('click', () => {
      btnVisaoArvore.classList.add('ativo');
      btnVisaoDiagrama.classList.remove('ativo');
      arvoreConteiner.style.display = 'block';
      diagramaConteiner.style.display = 'none';
    });

    btnVisaoDiagrama.addEventListener('click', () => {
      btnVisaoDiagrama.classList.add('ativo');
      btnVisaoArvore.classList.remove('ativo');
      arvoreConteiner.style.display = 'none';
      diagramaConteiner.style.display = 'flex';
      renderizarDiagramaSVG(noSelecionado || DADOS.arvore);
    });

    btnExpandirTudo.addEventListener('click', () => {
      document.querySelectorAll('.tree-node-filhos').forEach(el => el.style.display = 'block');
      document.querySelectorAll('.tree-expander').forEach(el => el.textContent = '▼');
    });

    btnRecolherTudo.addEventListener('click', () => {
      document.querySelectorAll('.tree-node-filhos').forEach((el, idx) => {
        // Mantém a raiz aberta
        if (idx > 0) el.style.display = 'none';
      });
      document.querySelectorAll('.tree-expander').forEach((el, idx) => {
        if (idx > 0) el.textContent = '▶';
      });
    });

    chkModoCompacto.addEventListener('change', () => {
      renderizarArvoreSintatica();
      if (btnVisaoDiagrama.classList.contains('ativo')) {
        renderizarDiagramaSVG(noSelecionado || DADOS.arvore);
      }
    });

    renderizarArvoreSintatica();
  }

  function renderizarArvoreSintatica() {
    arvoreConteiner.innerHTML = '';
    const raizElemento = criarElementoNoArvore(DADOS.arvore, 0);
    arvoreConteiner.appendChild(raizElemento);
  }

  function criarElementoNoArvore(no, profundidade) {
    if (!no) return document.createDocumentFragment();

    // Modo compacto: oculta quebras de linha avulsas
    if (chkModoCompacto.checked && no.nome === 'nova_linha') {
      return document.createDocumentFragment();
    }

    const conteiner = document.createElement('div');
    conteiner.className = 'tree-node';
    conteiner.dataset.nodeId = no.id;

    const row = document.createElement('div');
    row.className = 'tree-row';
    row.id = `tree-row-${no.id}`;

    const temFilhos = no.filhos && no.filhos.length > 0;
    const expander = document.createElement('span');
    expander.className = 'tree-expander';
    expander.textContent = temFilhos ? '▼' : ' ';

    let badgeIcone = '📂';
    let badgeHtml = '';

    if (no.tipo === 'token') {
      badgeIcone = '🍃';
      badgeHtml = `<span class="tree-badge-token">${escapeHtml(no.nome)}: <code>${escapeHtml(JSON.stringify(no.texto))}</code></span>`;
    } else if (no.tipo === 'erro') {
      badgeIcone = '⚠️';
      badgeHtml = `<span class="tree-badge-erro">Erro Sintático: ${escapeHtml(no.texto || 'símbolo inesperado')}</span>`;
    } else {
      // Regra
      if (no.rotulo) {
        badgeHtml = `<span class="tree-badge-regra">${escapeHtml(no.nome)}</span> · <span class="tree-badge-rotulo">#${escapeHtml(no.rotulo)}</span>`;
      } else {
        badgeHtml = `<span class="tree-badge-regra">${escapeHtml(no.nome)}</span>`;
      }
    }

    const posBadge = document.createElement('span');
    posBadge.style.cssText = 'color: var(--texto-fraco); font-size: 10px; margin-left: auto;';
    posBadge.textContent = `L${no.linha_inicio}:C${no.coluna_inicio}-L${no.linha_fim}:C${no.coluna_fim}`;

    row.innerHTML = `<span class="tree-expander">${expander.textContent}</span> <span>${badgeIcone}</span> ${badgeHtml}`;
    row.appendChild(posBadge);

    conteiner.appendChild(row);

    let filhosDiv = null;
    if (temFilhos) {
      filhosDiv = document.createElement('div');
      filhosDiv.className = 'tree-node-filhos';
      filhosDiv.style.display = 'block';

      no.filhos.forEach(filho => {
        filhosDiv.appendChild(criarElementoNoArvore(filho, profundidade + 1));
      });
      conteiner.appendChild(filhosDiv);
    }

    // Toggle expandir/recolher
    const expanderEl = row.querySelector('.tree-expander');
    expanderEl.addEventListener('click', e => {
      e.stopPropagation();
      if (!temFilhos || !filhosDiv) return;
      const aberto = filhosDiv.style.display !== 'none';
      filhosDiv.style.display = aberto ? 'none' : 'block';
      expanderEl.textContent = aberto ? '▶' : '▼';
    });

    // Clique no nó da árvore: seleciona e destaca código
    row.addEventListener('click', () => {
      selecionarNoArvore(no, row);
    });

    return conteiner;
  }

  function selecionarNoArvore(no, rowElemento) {
    document.querySelectorAll('.tree-row.selecionado').forEach(r => r.classList.remove('selecionado'));
    if (rowElemento) rowElemento.classList.add('selecionado');
    noSelecionado = no;

    // Destaca o trecho no código-fonte
    document.querySelectorAll('.codigo-linha.destaque-linha').forEach(l => l.classList.remove('destaque-linha'));
    for (let l = no.linha_inicio; l <= no.linha_fim; l++) {
      const linhaDiv = document.getElementById(`cod-linha-${l}`);
      if (linhaDiv) linhaDiv.classList.add('destaque-linha');
    }
    scrollParaLinha(no.linha_inicio);

    // Se a visão de diagrama estiver aberta, atualiza para o nó selecionado
    if (btnVisaoDiagrama.classList.contains('ativo')) {
      renderizarDiagramaSVG(no);
    }
  }

  // 5. Renderizador de Diagrama em SVG Hierárquico com Pan & Zoom
  function renderizarDiagramaSVG(noRaiz) {
    if (!noRaiz) return;
    diagramaConteiner.innerHTML = '';

    // Barra de ferramentas superior do diagrama
    const barraFerramentas = document.createElement('div');
    barraFerramentas.className = 'diagrama-barra-ferramentas';
    barraFerramentas.innerHTML = `
      <div class="diagrama-info-subarvore">
        <span>Subárvore: <strong>${escapeHtml(noRaiz.rotulo || noRaiz.nome)}</strong> (Linha ${noRaiz.linha_inicio})</span>
        ${noRaiz !== DADOS.arvore ? '<button class="btn-acao pequeno" id="btn-reset-diagrama">Voltar para Raiz</button>' : ''}
      </div>
      <div class="dica-navegacao">
        <span>🖐️ Arraste para mover</span>
        <span>&bull;</span>
        <span>🔍 Roda do mouse para zoom</span>
      </div>
      <div class="diagrama-controles-zoom">
        <button class="btn-acao pequeno" id="btn-zoom-menos" title="Diminuir zoom (Roda para trás)">➖</button>
        <span class="badge-zoom" id="zoom-indicador" title="Clique para resetar em 100%">100%</span>
        <button class="btn-acao pequeno" id="btn-zoom-mais" title="Aumentar zoom (Roda para frente)">➕</button>
        <button class="btn-acao pequeno" id="btn-zoom-ajustar" title="Ajustar diagrama à tela">Ajustar</button>
        <button class="btn-acao pequeno" id="btn-zoom-reset" title="Tamanho original 100%">1:1</button>
      </div>
    `;
    diagramaConteiner.appendChild(barraFerramentas);

    const btnResetDiagrama = barraFerramentas.querySelector('#btn-reset-diagrama');
    if (btnResetDiagrama) {
      btnResetDiagrama.addEventListener('click', () => {
        renderizarDiagramaSVG(DADOS.arvore);
      });
    }

    // Área do canvas com SVG interativo
    const canvasArea = document.createElement('div');
    canvasArea.className = 'diagrama-canvas-area';
    diagramaConteiner.appendChild(canvasArea);

    // Calcula posições dos nós em árvore hierárquica
    const nosPlanos = [];
    const conexoes = [];
    let proximoX = 50;

    function calcularLayout(nodo, nivel) {
      const filhosValidos = (nodo.filhos || []).filter(f => !chkModoCompacto.checked || f.nome !== 'nova_linha');
      const nodoLayout = {
        dado: nodo,
        nivel: nivel,
        y: 50 + nivel * 75,
        x: 0,
        filhos: []
      };
      nosPlanos.push(nodoLayout);

      if (filhosValidos.length === 0) {
        nodoLayout.x = proximoX;
        proximoX += 135;
      } else {
        filhosValidos.forEach(f => {
          const fLayout = calcularLayout(f, nivel + 1);
          nodoLayout.filhos.push(fLayout);
          conexoes.push({ de: nodoLayout, para: fLayout });
        });
        nodoLayout.x = (nodoLayout.filhos[0].x + nodoLayout.filhos[nodoLayout.filhos.length - 1].x) / 2;
      }
      return nodoLayout;
    }

    const layoutRaiz = calcularLayout(noRaiz, 0);
    const larguraDiagrama = Math.max(600, proximoX + 50);
    const alturaDiagrama = Math.max(...nosPlanos.map(n => n.y)) + 60;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'diagrama-svg');

    // Defs para grid pontilhado
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = `
      <pattern id="diag-grid" width="30" height="30" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1" fill="#333c56" />
      </pattern>
    `;
    svg.appendChild(defs);

    // Fundo com grid para orientação espacial ao arrastar
    const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bgRect.setAttribute('width', '100%');
    bgRect.setAttribute('height', '100%');
    bgRect.setAttribute('fill', 'url(#diag-grid)');
    svg.appendChild(bgRect);

    // Viewport que recebe as transformações de Pan & Zoom
    const viewport = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    viewport.setAttribute('class', 'diagrama-viewport');
    svg.appendChild(viewport);

    // Desenha arestas conectadas por curvas suaves
    conexoes.forEach(c => {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const d = `M ${c.de.x} ${c.de.y + 15} C ${c.de.x} ${(c.de.y + c.para.y) / 2}, ${c.para.x} ${(c.de.y + c.para.y) / 2}, ${c.para.x} ${c.para.y - 15}`;
      path.setAttribute('d', d);
      path.setAttribute('stroke', '#3b4261');
      path.setAttribute('stroke-width', '2');
      path.setAttribute('fill', 'none');
      viewport.appendChild(path);
    });

    // Desenha nós interativos
    nosPlanos.forEach(n => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'diagrama-no-svg');
      g.setAttribute('transform', `translate(${n.x}, ${n.y})`);

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', '-55');
      rect.setAttribute('y', '-15');
      rect.setAttribute('width', '110');
      rect.setAttribute('height', '30');
      rect.setAttribute('rx', '6');

      let corBorda = '#4c566a';
      let corFundo = '#1e2233';
      let corTexto = '#e2e8f0';

      if (n.dado.tipo === 'token') {
        corBorda = '#10b981';
        corFundo = '#064e3b';
      } else if (n.dado.tipo === 'erro') {
        corBorda = '#ef4444';
        corFundo = '#7f1d1d';
      } else if (n.dado.rotulo) {
        corBorda = '#8b5cf6';
        corFundo = '#3b1d6b';
      }

      rect.setAttribute('fill', corFundo);
      rect.setAttribute('stroke', corBorda);
      rect.setAttribute('stroke-width', '1.5');

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'central');
      text.setAttribute('fill', corTexto);
      text.setAttribute('font-size', '11');
      text.setAttribute('font-family', 'var(--fonte-mono)');

      const label = n.dado.rotulo || (n.dado.tipo === 'token' ? `"${n.dado.texto}"` : n.dado.nome);
      text.textContent = label.length > 13 ? label.slice(0, 11) + '..' : label;

      g.appendChild(rect);
      g.appendChild(text);

      g.addEventListener('click', e => {
        if (arrastou) return;
        e.stopPropagation();
        selecionarNoArvore(n.dado, document.getElementById(`tree-row-${n.dado.id}`));
      });

      viewport.appendChild(g);
    });

    canvasArea.appendChild(svg);

    // Estado e Controle de Pan & Zoom
    let scale = 1.0;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let arrastou = false;
    let startX = 0;
    let startY = 0;
    let startTransX = 0;
    let startTransY = 0;

    const zoomIndicador = barraFerramentas.querySelector('#zoom-indicador');
    const btnZoomMais = barraFerramentas.querySelector('#btn-zoom-mais');
    const btnZoomMenos = barraFerramentas.querySelector('#btn-zoom-menos');
    const btnZoomAjustar = barraFerramentas.querySelector('#btn-zoom-ajustar');
    const btnZoomReset = barraFerramentas.querySelector('#btn-zoom-reset');

    function aplicarTransform() {
      viewport.setAttribute('transform', `translate(${translateX}, ${translateY}) scale(${scale})`);
      zoomIndicador.textContent = `${Math.round(scale * 100)}%`;
    }

    function zoomNoPonto(screenX, screenY, fator) {
      const novoScale = Math.min(4.0, Math.max(0.15, scale * fator));
      if (Math.abs(novoScale - scale) < 0.001) return;
      const rect = svg.getBoundingClientRect();
      const mx = screenX - rect.left;
      const my = screenY - rect.top;
      const diagX = (mx - translateX) / scale;
      const diagY = (my - translateY) / scale;
      translateX = mx - diagX * novoScale;
      translateY = my - diagY * novoScale;
      scale = novoScale;
      aplicarTransform();
    }

    function zoomPeloCentro(fator) {
      const rect = svg.getBoundingClientRect();
      zoomNoPonto(rect.left + rect.width / 2, rect.top + rect.height / 2, fator);
    }

    function ajustarAoEcra() {
      const rect = canvasArea.getBoundingClientRect();
      const larguraCanvas = rect.width || 800;
      const alturaCanvas = rect.height || 500;
      const pad = 40;
      const escalaX = (larguraCanvas - pad * 2) / larguraDiagrama;
      const escalaY = (alturaCanvas - pad * 2) / alturaDiagrama;
      let novaEscala = Math.min(1.2, Math.max(0.2, Math.min(escalaX, escalaY)));
      scale = novaEscala;
      translateX = (larguraCanvas - larguraDiagrama * scale) / 2;
      translateY = Math.max(30, (alturaCanvas - alturaDiagrama * scale) / 2);
      aplicarTransform();
    }

    function resetarZoom() {
      const rect = canvasArea.getBoundingClientRect();
      const larguraCanvas = rect.width || 800;
      scale = 1.0;
      translateX = Math.max(30, (larguraCanvas - larguraDiagrama) / 2);
      translateY = 40;
      aplicarTransform();
    }

    // Zoom via roda do mouse (para frente / para trás)
    svg.addEventListener('wheel', e => {
      e.preventDefault();
      const fator = e.deltaY < 0 ? 1.15 : 0.87;
      zoomNoPonto(e.clientX, e.clientY, fator);
    }, { passive: false });

    // Arrastar (pan) com mouse / toque via Pointer Events
    svg.addEventListener('pointerdown', e => {
      if (e.button !== 0) return;
      isDragging = true;
      arrastou = false;
      startX = e.clientX;
      startY = e.clientY;
      startTransX = translateX;
      startTransY = translateY;
      svg.classList.add('arrastando');
      svg.setPointerCapture(e.pointerId);
    });

    svg.addEventListener('pointermove', e => {
      if (!isDragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        arrastou = true;
      }
      translateX = startTransX + dx;
      translateY = startTransY + dy;
      aplicarTransform();
    });

    function finalizarDrag(e) {
      if (isDragging) {
        isDragging = false;
        svg.classList.remove('arrastando');
        try {
          svg.releasePointerCapture(e.pointerId);
        } catch (_) {}
      }
    }

    svg.addEventListener('pointerup', finalizarDrag);
    svg.addEventListener('pointercancel', finalizarDrag);

    // Duplo clique no fundo ajusta ao enquadramento
    svg.addEventListener('dblclick', e => {
      if (e.target === svg || e.target === bgRect) {
        ajustarAoEcra();
      }
    });

    // Ações dos botões da barra de ferramentas
    btnZoomMais.addEventListener('click', () => zoomPeloCentro(1.25));
    btnZoomMenos.addEventListener('click', () => zoomPeloCentro(0.8));
    btnZoomAjustar.addEventListener('click', () => ajustarAoEcra());
    btnZoomReset.addEventListener('click', () => resetarZoom());
    zoomIndicador.addEventListener('click', () => resetarZoom());

    // Enquadramento inicial automático após o elemento estar visível
    requestAnimationFrame(() => {
      ajustarAoEcra();
    });
  }

  // 6. Aba Narrativa: Entidades, Grafo de Marcos e Operações
  const narrativaConteudo = document.getElementById('narrativa-conteudo');

  const ICONES_ENTIDADE = {
    universo: '🌍',
    campanha: '📜',
    jogador: '👤',
    personagem: '👤',
    historia: '📖',
    marco: '🚩',
    capitulo: '🏛️',
    cena: '🎬',
    cenario: '🗺️',
    item: '🎒'
  };

  function initAbaNarrativa() {
    const est = DADOS.estrutura || {};
    narrativaConteudo.innerHTML = '';

    if (!est.entidades || (est.entidades.length === 0 && (!est.marcos || est.marcos.length === 0))) {
      narrativaConteudo.innerHTML = `
        <div style="padding: 20px; text-align: center; color: var(--texto-fraco); font-size: 13px;">
          Nenhuma entidade ou estrutura narrativa encontrada neste programa.
        </div>
      `;
      return;
    }

    // 1. Ponto de Entrada da Sessão (iniciar campanha com historia)
    if (est.iniciar) {
      const cardIniciar = document.createElement('div');
      cardIniciar.className = 'cartao-iniciar-destaque';
      cardIniciar.innerHTML = `
        <div style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #a78bfa; margin-bottom: 4px;">
          🎮 Ponto de Entrada da Sessão Interativa
        </div>
        <div style="font-family: var(--fonte-mono); font-size: 13px; font-weight: 600;">
          iniciar <span style="color: #60a5fa;">${escapeHtml(est.iniciar.campanha)}</span> com <span style="color: #34d399;">${escapeHtml(est.iniciar.historia)}</span>
        </div>
      `;
      narrativaConteudo.appendChild(cardIniciar);
    }

    // 2. Grafo de Marcos Narrativos
    if (est.marcos && est.marcos.length > 0) {
      const secaoMarcos = document.createElement('div');
      secaoMarcos.className = 'secao-narrativa';
      secaoMarcos.innerHTML = `
        <div class="secao-narrativa-titulo">
          <span>🚩</span> Rede de Marcos Narrativos (${est.marcos.length})
        </div>
      `;

      // Renderiza grafo SVG de dependência dos marcos
      const grafoSvg = renderizarGrafoMarcosSVG(est.marcos, est.encerramentos || []);
      secaoMarcos.appendChild(grafoSvg);
      narrativaConteudo.appendChild(secaoMarcos);
    }

    // 3. Operações Narrativas
    if (est.operacoes && est.operacoes.length > 0) {
      const secaoOp = document.createElement('div');
      secaoOp.className = 'secao-narrativa';
      secaoOp.innerHTML = `
        <div class="secao-narrativa-titulo">
          <span>⚡</span> Operações Narrativas Disponíveis (${est.operacoes.length})
        </div>
      `;

      est.operacoes.forEach(op => {
        const cardOp = document.createElement('div');
        cardOp.className = 'cartao-operacao';
        cardOp.title = 'Clique para ver no código';

        let instrucoesHtml = '';
        if (op.instrucoes && op.instrucoes.length > 0) {
          instrucoesHtml = `
            <div style="margin-top: 6px; font-size: 11px; color: var(--texto-fraco); font-weight: 600;">Efeitos confirmados:</div>
            <div class="lista-instrucoes-op">
              ${op.instrucoes.map(ins => `<div>• ${escapeHtml(ins)}</div>`).join('')}
            </div>
          `;
        }

        cardOp.innerHTML = `
          <div class="operacao-header">
            <span class="operacao-nome">operacao ${escapeHtml(op.caminho)}</span>
            <span class="badge-requer">requer ${escapeHtml(op.requer)}</span>
          </div>
          ${instrucoesHtml}
        `;

        cardOp.addEventListener('click', () => {
          scrollParaLinha(op.linha);
        });

        secaoOp.appendChild(cardOp);
      });

      narrativaConteudo.appendChild(secaoOp);
    }

    // 4. Árvore de Entidades do RPG
    if (est.entidades && est.entidades.length > 0) {
      const secaoEnt = document.createElement('div');
      secaoEnt.className = 'secao-narrativa';
      secaoEnt.innerHTML = `
        <div class="secao-narrativa-titulo">
          <span>🌍</span> Hierarquia de Entidades Declaradas
        </div>
      `;

      est.entidades.forEach(ent => {
        secaoEnt.appendChild(criarElementoEntidade(ent, 0));
      });

      narrativaConteudo.appendChild(secaoEnt);
    }
  }

  function renderizarGrafoMarcosSVG(marcos, encerramentos) {
    const conteiner = document.createElement('div');
    conteiner.style.cssText = 'background: var(--bg-painel); border: 1px solid var(--borda); border-radius: 8px; padding: 12px; overflow-x: auto;';

    const largura = Math.max(700, marcos.length * 230 + 100);
    const altura = 180;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', largura);
    svg.setAttribute('height', altura);

    const posicoes = {};
    marcos.forEach((m, idx) => {
      posicoes[m.variavel] = {
        x: 120 + idx * 220,
        y: 80,
        dado: m
      };
    });

    // Marcador de seta SVG
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'seta-dependencia');
    marker.setAttribute('viewBox', '0 0 10 10');
    marker.setAttribute('refX', '10');
    marker.setAttribute('refY', '5');
    marker.setAttribute('markerWidth', '6');
    marker.setAttribute('markerHeight', '6');
    marker.setAttribute('orient', 'auto-start-reverse');
    const pathSeta = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathSeta.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
    pathSeta.setAttribute('fill', '#a78bfa');
    marker.appendChild(pathSeta);
    defs.appendChild(marker);
    svg.appendChild(defs);

    // Desenha arestas de dependência
    marcos.forEach(m => {
      const posDestino = posicoes[m.variavel];
      (m.dependencias || []).forEach(depNome => {
        const posOrigem = posicoes[depNome];
        if (posOrigem && posDestino) {
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          const d = `M ${posOrigem.x + 85} ${posOrigem.y} L ${posDestino.x - 85} ${posDestino.y}`;
          path.setAttribute('d', d);
          path.setAttribute('stroke', '#8b5cf6');
          path.setAttribute('stroke-width', '2');
          path.setAttribute('marker-end', 'url(#seta-dependencia)');
          svg.appendChild(path);
        }
      });
    });

    // Desenha nós de marcos
    Object.values(posicoes).forEach(p => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${p.x}, ${p.y})`);
      g.style.cursor = 'pointer';

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', '-85');
      rect.setAttribute('y', '-32');
      rect.setAttribute('width', '170');
      rect.setAttribute('height', '64');
      rect.setAttribute('rx', '8');
      rect.setAttribute('fill', '#1e2233');
      rect.setAttribute('stroke', '#a78bfa');
      rect.setAttribute('stroke-width', '1.5');

      const titulo = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      titulo.setAttribute('x', '0');
      titulo.setAttribute('y', '-12');
      titulo.setAttribute('text-anchor', 'middle');
      titulo.setAttribute('fill', '#f1f5f9');
      titulo.setAttribute('font-size', '12');
      titulo.setAttribute('font-weight', 'bold');
      titulo.textContent = `🚩 ${p.dado.variavel}`;

      const cond = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      cond.setAttribute('x', '0');
      cond.setAttribute('y', '12');
      cond.setAttribute('text-anchor', 'middle');
      cond.setAttribute('fill', '#94a3b8');
      cond.setAttribute('font-size', '10');
      cond.setAttribute('font-family', 'var(--fonte-mono)');
      const condTexto = p.dado.condicao ? `quando ${p.dado.condicao}` : '(sem condicao)';
      cond.textContent = condTexto.length > 24 ? condTexto.slice(0, 22) + '..' : condTexto;

      g.appendChild(rect);
      g.appendChild(titulo);
      g.appendChild(cond);

      g.addEventListener('click', () => {
        scrollParaLinha(p.dado.linha);
      });

      svg.appendChild(g);
    });

    conteiner.appendChild(svg);

    if (encerramentos && encerramentos.length > 0) {
      const encDiv = document.createElement('div');
      encDiv.style.cssText = 'margin-top: 10px; font-size: 11px; color: var(--texto-secundario); font-family: var(--fonte-mono); border-top: 1px solid var(--borda-suave); padding-top: 8px;';
      encDiv.innerHTML = `
        <strong>Critério de Encerramento:</strong> ${encerramentos.map(e => `encerrar <span style="color: #c084fc;">${escapeHtml(e.historia)}</span> quando <span style="color: #fbbf24;">${escapeHtml(e.condicao)}</span>`).join('; ')}
      `;
      conteiner.appendChild(encDiv);
    }

    return conteiner;
  }

  function criarElementoEntidade(ent, profundidade) {
    const card = document.createElement('div');
    card.className = 'cartao-entidade';
    card.style.marginLeft = `${profundidade * 16}px`;

    const icone = ICONES_ENTIDADE[ent.tipo] || '📦';
    const nomeVisual = ent.propriedades.nome || ent.id;

    let propsHtml = '';
    const propChaves = Object.keys(ent.propriedades).filter(k => k !== 'nome');
    if (propChaves.length > 0) {
      propsHtml = `
        <div class="cartao-propriedades">
          ${propChaves.map(k => `<div><strong>${escapeHtml(k)}:</strong> ${escapeHtml(ent.propriedades[k])}</div>`).join('')}
        </div>
      `;
    }

    let estadosHtml = '';
    if (ent.estados && ent.estados.length > 0) {
      estadosHtml = `
        <table class="tabela-estados-mini">
          <thead>
            <tr><th>Tipo</th><th>Campo</th><th>Valor Inicial</th></tr>
          </thead>
          <tbody>
            ${ent.estados.map(e => `
              <tr>
                <td style="color: #60a5fa;">${escapeHtml(e.tipo)}</td>
                <td style="color: #38bdf8;">${escapeHtml(e.caminho)}</td>
                <td style="color: #34d399;">${escapeHtml(e.valor)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    card.innerHTML = `
      <div class="cartao-header">
        <div class="cartao-titulo">
          <span>${icone}</span>
          <span>${escapeHtml(nomeVisual)}</span>
          <span style="font-size: 11px; font-family: var(--fonte-mono); color: var(--texto-fraco);">(${escapeHtml(ent.variavel)})</span>
        </div>
        <span class="badge-tipo-entidade">${escapeHtml(ent.tipo)}</span>
      </div>
      ${propsHtml}
      ${estadosHtml}
    `;

    if (ent.filhos && ent.filhos.length > 0) {
      const filhosConteiner = document.createElement('div');
      filhosConteiner.style.marginTop = '10px';
      ent.filhos.forEach(f => {
        filhosConteiner.appendChild(criarElementoEntidade(f, profundidade + 1));
      });
      card.appendChild(filhosConteiner);
    }

    return card;
  }

  // 6. Aba Semântica e Runtime (E4)
  function initAbaSemantica() {
    const conteiner = document.getElementById('semantico-conteudo');
    if (!conteiner) return;

    const sem = DADOS.semantico;
    if (!sem || !sem.variaveis) {
      conteiner.innerHTML = `<div style="color: var(--texto-fraco); padding: 20px;">Nenhum dado semântico gerado. Certifique-se de que a análise sintática passou sem erros.</div>`;
      return;
    }

    let varsHtml = `
      <div style="margin-bottom: 24px;">
        <h3 style="font-size: 14px; color: var(--cor-primaria); margin-bottom: 8px;">🏷️ Tabela de Símbolos e Escopos (${sem.variaveis.length} identificadores)</h3>
        <table class="tabela-tokens" style="width: 100%;">
          <thead>
            <tr>
              <th>Variável</th>
              <th>Tipo</th>
              <th>ID Instância</th>
              <th>Receptor Pai</th>
              <th>Campos de Estado / Ficha</th>
            </tr>
          </thead>
          <tbody>
            ${sem.variaveis.map(v => {
              const campos = [
                ...v.estado.map(e => `[estado] ${e.campo}: ${e.tipo}`),
                ...v.ficha.map(f => `[ficha] ${f.campo}: ${f.tipo}`)
              ].join(', ');
              return `
                <tr>
                  <td style="color: #38bdf8; font-weight: bold;">${escapeHtml(v.variavel)}</td>
                  <td><span class="badge-tipo-entidade">${escapeHtml(v.tipo)}</span></td>
                  <td style="color: #34d399;">"${escapeHtml(v.id || '')}"</td>
                  <td style="color: var(--texto-secundario);">${escapeHtml(v.pai || '-')}</td>
                  <td style="color: #60a5fa; font-size: 11px;">${escapeHtml(campos || 'nenhum')}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;

    let marcosHtml = `
      <div style="margin-bottom: 24px;">
        <h3 style="font-size: 14px; color: #10b981; margin-bottom: 8px;">🎯 Grafo de Marcos Narrativos (${sem.marcos.length} marcos validados)</h3>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          ${sem.marcos.map(m => `
            <div style="background: var(--bg-cartao); border: 1px solid var(--borda); border-radius: 6px; padding: 10px; min-width: 200px;">
              <div style="font-weight: bold; color: #34d399;">Marco: ${escapeHtml(m.id)} (${escapeHtml(m.variavel)})</div>
              <div style="font-size: 11px; color: var(--texto-fraco);">História: ${escapeHtml(m.historia)}</div>
              <div style="font-size: 11px; margin-top: 6px; color: #fbbf24;">
                Depende de: ${m.dependencias && m.dependencias.length > 0 ? m.dependencias.map(d => `<code>${escapeHtml(d)}</code>`).join(', ') : '<em>raiz (nenhuma)</em>'}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    let opsHtml = `
      <div>
        <h3 style="font-size: 14px; color: #c084fc; margin-bottom: 8px;">⚡ Operações Narrativas Declaradas (${sem.operacoes.length})</h3>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          ${sem.operacoes.map(op => `
            <div style="background: var(--bg-cartao); border: 1px solid var(--borda); border-radius: 6px; padding: 10px; min-width: 220px;">
              <div style="font-weight: bold; color: #c084fc;">${escapeHtml(op.caminho)}</div>
              <div style="font-size: 11px; color: var(--texto-fraco);">Vinculado à história: ${escapeHtml(op.historia)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    conteiner.innerHTML = varsHtml + marcosHtml + opsHtml;
  }

  // Listeners de navegação de abas
  document.querySelectorAll('.aba-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      ativarAba(btn.dataset.aba);
    });
  });

  chkMostrarLayout.addEventListener('change', () => {
    renderizarTabelaTokens();
  });

  // Inicializa tudo
  initHeader();
  renderizarCodigoFonte();
  initAbaLexica();
  initAbaSintatica();
  initAbaNarrativa();
  initAbaSemantica();

  // Expõe no escopo global
  window.CompiladorVisual = {
    DADOS,
    escapeHtml,
    destacarToken,
    removerDestaqueToken,
    scrollParaLinha,
    ativarAba,
    selecionarNoArvore
  };
})();



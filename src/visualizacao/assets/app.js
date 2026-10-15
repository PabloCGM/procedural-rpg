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
      diagramaConteiner.style.display = 'block';
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

  // 5. Renderizador de Diagrama em SVG Hierárquico Puro
  function renderizarDiagramaSVG(noRaiz) {
    if (!noRaiz) return;
    diagramaConteiner.innerHTML = '';

    const cabecalhoInfo = document.createElement('div');
    cabecalhoInfo.style.cssText = 'font-size: 12px; color: var(--texto-secundario); margin-bottom: 12px; display: flex; justify-content: space-between;';
    cabecalhoInfo.innerHTML = `
      <span>Exibindo subárvore: <strong>${escapeHtml(noRaiz.rotulo || noRaiz.nome)}</strong> (Linha ${noRaiz.linha_inicio})</span>
      <button class="btn-acao pequeno" id="btn-reset-diagrama">Voltar para Raiz</button>
    `;
    diagramaConteiner.appendChild(cabecalhoInfo);

    cabecalhoInfo.querySelector('#btn-reset-diagrama').addEventListener('click', () => {
      renderizarDiagramaSVG(DADOS.arvore);
    });

    // Calcula posições dos nós em árvore compacta
    const nosPlanos = [];
    const conexoes = [];
    let proximoX = 40;

    function calcularLayout(nodo, nivel) {
      const filhosValidos = (nodo.filhos || []).filter(f => !chkModoCompacto.checked || f.nome !== 'nova_linha');
      const nodoLayout = {
        dado: nodo,
        nivel: nivel,
        y: 40 + nivel * 70,
        x: 0,
        filhos: []
      };
      nosPlanos.push(nodoLayout);

      if (filhosValidos.length === 0) {
        nodoLayout.x = proximoX;
        proximoX += 130;
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

    const larguraSvg = Math.max(800, proximoX + 60);
    const maxY = Math.max(...nosPlanos.map(n => n.y)) + 60;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', larguraSvg);
    svg.setAttribute('height', maxY);
    svg.style.cssText = 'background: var(--bg-painel); border-radius: 8px; border: 1px solid var(--borda);';

    // Desenha arestas conectadas por curvas suaves
    conexoes.forEach(c => {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const d = `M ${c.de.x} ${c.de.y + 15} C ${c.de.x} ${(c.de.y + c.para.y) / 2}, ${c.para.x} ${(c.de.y + c.para.y) / 2}, ${c.para.x} ${c.para.y - 15}`;
      path.setAttribute('d', d);
      path.setAttribute('stroke', '#3b4261');
      path.setAttribute('stroke-width', '2');
      path.setAttribute('fill', 'none');
      svg.appendChild(path);
    });

    // Desenha nós
    nosPlanos.forEach(n => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${n.x}, ${n.y})`);
      g.style.cursor = 'pointer';

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

      g.addEventListener('click', () => {
        selecionarNoArvore(n.dado, document.getElementById(`tree-row-${n.dado.id}`));
      });

      svg.appendChild(g);
    });

    diagramaConteiner.appendChild(svg);
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

  // Listeners de navegação de abas
  document.querySelectorAll('.aba-btn:not(.desabilitada)').forEach(btn => {
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



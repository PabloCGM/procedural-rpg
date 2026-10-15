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

  // Expõe no escopo global para que as abas Sintática e Narrativa dos Passos 4 e 5 se acoplem facilmente
  window.CompiladorVisual = {
    DADOS,
    escapeHtml,
    destacarToken,
    removerDestaqueToken,
    scrollParaLinha,
    ativarAba
  };
})();

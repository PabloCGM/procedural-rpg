# Diário de desenvolvimento

<!-- A cada sessão, adicionar uma entrada com data, o que foi tentado e o que aconteceu. -->

## 16/09/2026 — Parte B: análise léxica

Implementamos as regras de lexer do Procedural RPG em ANTLR 4.13.2 e o comando Python
para listar tokens e localizar erros. A gramática descarta comentários e espaços;
usamos as posições de linha e coluna preservadas pelo ANTLR para reconstruir os
níveis de indentação em uma etapa de layout, sem introduzir regras de parser.

Números como `1.2.3` e `12abc` precisavam ser diagnosticados como malformados, em vez
de aceitos como fragmentos válidos. Regras de erro capturam essas sequências e textos
com escapes inválidos ou sem fechamento; o programa continua buscando outros erros.

Geramos o lexer, instalamos o runtime da mesma versão em um ambiente virtual local
e passamos os 22 testes de reconhecimento, layout, diagnósticos e interface de terminal,
incluindo o programa completo da Parte A. O PowerShell deste ambiente bloqueou o script
de geração; o comando direto do ANTLR funcionou sem alterar a política do sistema.

## 16/09/2026 — Parte B: fechamento

Tentamos validar a gramática com `antlr4-parse SuaLing.g4 programa -tokens`, como
sugere o enunciado. Com `lexer grammar`, o `antlr4-parse` 4.13.2 lança
`ClassCastException` antes de ler a entrada; um arquivo de parser auxiliar com
`tokenVocab` não contornou o problema. Trocar o cabeçalho para `grammar SuaLing;`, como
no exemplo `Calc`, fez o `antlr4-parse` imprimir os tokens, mas a geração de código
falhou com "grammar SuaLing has no rules", porque não há regras de parser.
Mantivemos `lexer grammar` e usamos `src/lexico.py` para inspecionar os tokens.

Regeramos o lexer e rodamos novamente os 22 testes, todos aprovados. Conferimos o
programa da Parte A (416 tokens, código de saída 0) e um arquivo com número malformado,
caractere inválido e texto sem fechar: os três erros foram apontados com linha e
coluna, com código de saída 1.

## 16/09/2026 — Parte C: exemplos e organização do repositório

Escrevemos os três programas válidos com os nomes pedidos no enunciado. Como `ola`,
`quadrado` e `espiral` vêm do domínio de desenho, adaptamos o conteúdo ao RPG: uma
saudação mínima, uma ronda pelos quatro cantos de um pátio e uma descida em espiral.
Cada um exercita partes diferentes do léxico, como texto no estado, sinal negativo,
divisão, parênteses e `se`/`senao` aninhados.

No quadrado, quisemos usar módulo para voltar ao primeiro canto, mas a especificação
não tem `%`. Em vez de mudar a linguagem, o quarto lado zera a contagem dentro de um
`senao`.

Os comentários dos arquivos inválidos indicavam colunas calculadas à mão, e duas
estavam erradas: contamos 40 onde o `;` fica na coluna 38 e 32 onde o `.5` fica na
coluna 30. Corrigimos pela saída do analisador e passamos a testar linha, coluna e
mensagem exatas de cada inválido, para que o comentário e o comportamento não se
separem de novo.

A especificação definia a extensão `.prpg`, mas o enunciado usa `.ml` em todos os
exemplos. Adotamos `.ml` para ficar igual ao enunciado e renomeamos o programa da
Parte A para `exemplos/parte_a.ml`. Um teste compara esse arquivo com o programa da
especificação. Removemos os `.ml` vazios da estrutura inicial e deixamos o diário em
`docs/`, como na estrutura da seção 5. Os 25 testes passam.

## 15/10/2026 — Etapa E3: analisador sintático e árvore sintática

Implementamos a análise sintática completa da linguagem Procedural RPG usando ANTLR 4 e
separação de gramáticas com `parser grammar SuaLingParser;` importando o vocabulário
léxico via `options { tokenVocab = SuaLing; }`.

O parser recebe diretamente o fluxo de tokens sintetizados pelo motor de layout da E2
(`INDENTA`, `DEDENTA` e `NOVA_LINHA`), permitindo expressar blocos hierárquicos e regras de
entidades sem ambiguidade com espaços. Mapeamos os 8 níveis de precedência de operadores
na regra `expr`, cobrindo expressões aritméticas, relacionais e lógicas com rótulos de nós.

Criamos o módulo `src/analise_sintatica.py` e o CLI `src/sintatico.py` com a opção `--arvore`
para visualizar a árvore sintática concreta de forma hierárquica. Criamos 5 exemplos de
programas sintaticamente inválidos em `invalidos_sintaticos/` e expandimos a suíte de testes
para 33 testes automatizados (25 léxicos e 8 sintáticos), todos aprovados.

## 15/10/2026 — Ferramenta didática: visualizador web interativo do compilador

Desenvolvemos uma ferramenta visual e didática em HTML autônomo e offline (`src/visualizar.py`)
para inspecionar todo o pipeline do compilador no navegador:

1. Painel com código-fonte realçado diretamente pelos tokens do lexer (com números de linha,
   comentários preservados e marcadores visuais de erros com indicação precisa da coluna).
2. Stepper do pipeline no topo exibindo o status de cada fase (Léxica, Sintática, Narrativa
   e Semântica para a E4).
3. Aba Léxica: tabela filtrável por categorias com busca textual e destaque bidirecional
   (passar o mouse no token acende o código-fonte e vice-versa).
4. Aba Sintática: árvore sintática expansível/colapsável com modo compacto e diagrama gráfico
   SVG hierárquico conectando os nós da árvore.
5. Aba Narrativa: visualização de entidades declaradas (Universo, Campanhas, Histórias,
   Personagens), grafo SVG de dependência de marcos narrativos e catálogo de operações.
6. Refatoração de pipeline com parada preventiva em erros léxicos para evitar erros em cascata
   falsos no parser, além de tradução em português de mensagens de diagnóstico do ANTLR.

## 04/11/2026 — Etapa E4: análise semântica, runtime e simulador interativo

Implementamos o back-end completo do compilador e motor narrativo de Procedural RPG (E4):

1. **Sistema de Tipos e Tabela de Símbolos (`src/semantico/`):**
   - Criação de tipos primitivos (`inteiro`, `real`, `texto`, `booleano`) e de entidades (`Universo`, `Campanha`, `Historia`, etc.).
   - Resolução de escopo hierárquico e caminhos por ponto (`<entidade>.<colecao>.<id>` e `<objeto>.estado.<campo>`).
   - Verificação rigorosa de compatibilidade de tipos: promoção de inteiros para reais, proibição estrita de coerção entre número e texto em `+`, checagem de tipos numéricos em comparações relacionais e expressões estritamente booleanas em `requer`, `se`, `concluir` e `encerrar`.

2. **Analisador Semântico com ANTLR Visitor (`src/analise_semantica.py`):**
   - Abordagem em dois passes estáticos (`ColetorDeclaracoesVisitor` e `VerificadorTiposVisitor`).
   - Validação da tabela de métodos de criação permitidos por receptor (ex: proibir `campanha.cenario(...)`).
   - Algoritmo de busca em profundidade (DFS) para detecção formal de dependências cíclicas e auto-dependências entre marcos narrativos.
   - Validação de pertinência no comando `iniciar campanha com historia`.

3. **Interpretador e Motor de Execução RPG (`src/interpretador.py` e `src/executar.py`):**
   - Avaliador de expressões dinâmicas em memória.
   - Motor de sessão com reavaliação automática de marcos em cascata e encerramento permanente da história.
   - Execução transacional de operações narrativas com verificação de pré-requisito `requer`, emissão de falas `narrar` e suporte a condicionais `se`/`senao`.
   - CLI interativo no terminal e suporte a execução não interativa via `--script` e `--apenas-semantico`.

4. **Testes Automatizados e Consolidação:**
   - Adicionamos 7 novos programas de erro semântico à pasta única `invalidos/`.
   - Criamos `tests/test_semantico.py` e `tests/test_execucao.py`.
   - A suíte agora conta com 55 testes automatizados (25 léxicos, 8 sintáticos, 14 visuais, 5 semânticos e 3 de runtime), todos 100% aprovados.


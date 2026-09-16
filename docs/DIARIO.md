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

# Procedural RPG

## 1. Apresentação e exemplo

Linguagem orientada a objetos de domínio específico para campanhas de RPG: universos,
personagens, histórias, capítulos, marcos e operações narrativas. Usa referências por
ponto e blocos delimitados por indentação obrigatória de quatro espaços.

Trecho de declaração:

```text
mundo = Universo("cidade_memorias")
    nome = "Cidade das Memórias"
    descricao = "Uma cidade onde lembranças são comercializadas."

    helena = mundo.personagem("helena")
        nome = "Rainha Helena"
        descricao = "Governante da cidade."
        motivacao = "Preservar a estabilidade do reino."
```

A [especificação](docs/especificacao.md) define o comportamento da linguagem.
[exemplos/ola.ml](exemplos/ola.ml) é o menor programa completo; a seção 2 lista os demais exemplos.

## 2. Instalação e execução

Requisitos: Python 3.10 ou superior, Java disponível no comando `java` e acesso à
internet para a instalação inicial das dependências. Ambiente verificado: Python
3.13.2, Java 24, gerador ANTLR **4.13.2** e runtime Python **4.13.2**.
O pacote `antlr4-tools` tem versão própria, **0.2.2**; não é a versão da gramática.

No PowerShell, a partir da raiz do repositório, sem precisar ativar scripts:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\antlr4.exe -v 4.13.2 -Dlanguage=Python3 -Xexact-output-dir -o gerado gramatica/SuaLing.g4
.\.venv\Scripts\antlr4.exe -v 4.13.2 -Dlanguage=Python3 -visitor -lib gerado -Xexact-output-dir -o gerado gramatica/SuaLingParser.g4
.\.venv\Scripts\python.exe src/executar.py exemplos/ola.ml
```

Em Linux/macOS ou terminal com `sh`, usando o ambiente virtual:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
sh gerar.sh
python src/executar.py exemplos/ola.ml
```

Cada fase do compilador tem seu comando, todos recebendo o caminho de um programa `.ml`:

| Comando | Fase | O que faz |
|---|---|---|
| `python src/lexico.py <arquivo>` | E2 | Lista os tokens com linha e coluna. |
| `python src/sintatico.py --arvore <arquivo>` | E3 | Valida a sintaxe e mostra a árvore sintática. |
| `python src/executar.py --apenas-semantico <arquivo>` | E4 | Valida léxico, sintaxe e semântica e mostra a tabela de símbolos. |
| `python src/executar.py <arquivo>` | E4 | Valida tudo e inicia a sessão interativa de RPG. |
| `python src/executar.py --script <roteiro> <arquivo>` | E4 | Executa a sessão com os comandos de um arquivo de texto. |
| `python src/visualizar.py <arquivo>` | E2–E4 | Gera o painel HTML com todas as fases (seção 4). |

`gerar.sh` fixa a versão do gerador e produz o lexer e o parser (com visitor) em `gerado/`.
Há também `gerar.ps1` para PowerShell quando a execução de scripts estiver habilitada
e `antlr4` estiver no PATH; o comando direto acima funciona sem alterar essa política.
Na primeira geração, `antlr4-tools` pode baixar o JAR do ANTLR. Java não é necessário
para executar o código que já foi gerado.

Regere o código após modificar qualquer gramática. As regras léxicas ficam em
`gramatica/SuaLing.g4` e as sintáticas em `gramatica/SuaLingParser.g4`, que importa o
vocabulário do lexer com `tokenVocab`. O gerador e o runtime são mantidos na mesma versão, conforme a
[documentação oficial do alvo Python do ANTLR](https://github.com/antlr/antlr4/blob/4.13.2/doc/python-target.md).
Arquivos gerados e o ambiente virtual são ignorados pelo Git.

O arquivo é declarado como `lexer grammar`. Com `grammar SuaLing;` e nenhuma regra de
parser, o ANTLR 4.13.2 falha na geração com `error(99): grammar SuaLing has no rules`.
Nessa mesma versão, `antlr4-parse` (seção 6.1 do enunciado) lança `ClassCastException`
ao receber uma gramática somente léxica. Por isso, a inspeção rápida dos tokens é feita
com `src/lexico.py`, que também mostra a coluna e os erros. A separação em duas
gramáticas foi mantida na E3: o parser lê os tokens de layout produzidos pela E2.

### Saída e erros

Todos os comandos seguem os mesmos códigos de saída e escrevem os erros em `stderr`,
com linha e coluna. A análise para na primeira fase que encontrar erros, para não
gerar erros em cascata nas fases seguintes.

O `lexico.py` lista o nome, lexema, linha e coluna de cada token e imprime o total.
Linha e coluna começam em **1**. O lexema é exibido entre aspas, com quebras e escapes
representados de forma visível; seu valor não é interpretado pelo lexer.

Comentários e espaços são descartados. O módulo `src/analise_lexica.py` usa as posições
preservadas pelo ANTLR para produzir `NOVA_LINHA`, `INDENTA` e `DEDENTA`, ignorando linhas
vazias ou apenas comentadas. Fecha os blocos no fim do arquivo, mesmo sem uma quebra
final. O total inclui esses tokens de layout, mas exclui EOF e tokens inválidos.

Mensagens de erro vão para a saída de erros (`stderr`). O analisador procura outros
erros após o primeiro e pode listar os tokens válidos encontrados no arquivo inválido.

| Código de saída | Significado |
|---|---|
| `0` | Nenhum erro encontrado nas fases executadas. |
| `1` | Erros léxicos, de indentação, sintáticos ou semânticos, com linha e coluna. |
| `2` | Falha de argumentos, leitura do arquivo ou dependências/geração ausentes. |

Arquivos são lidos como UTF-8, com ou sem BOM. LF, CRLF e CR são normalizados para
preservar linhas e colunas; tabs fora de literais ou do conteúdo de comentários são
rejeitados. O recuo inicial deve ser zero, cada aumento deve ser de quatro espaços
e cada retorno deve corresponder a um nível anterior.

### Exemplos

Programas válidos, em `exemplos/`, todos analisados sem erros:

| Arquivo | O que mostra |
|---|---|
| [ola.ml](exemplos/ola.ml) | O menor programa completo: universo, jogador, história, marco e uma operação. |
| [quadrado.ml](exemplos/quadrado.ml) | Ronda pelos quatro cantos de um pátio: estado em texto, reais, `se`/`senao` aninhados, item e cena. |
| [espiral.ml](exemplos/espiral.ml) | Descida em espiral: marcos encadeados, estado do universo, `/`, sinal negativo, parênteses, `e`/`ou`/`nao`. |
| [parte_a.ml](exemplos/parte_a.ml) | O programa comentado da especificação. |

Programas inválidos, em `invalidos/`, cada um com um único erro, indicado no comentário
do próprio arquivo. Todos terminam com código de saída `1`:

| Arquivo | Fase | Erro apontado |
|---|---|---|
| [caractere_invalido.ml](invalidos/caractere_invalido.ml) | léxica | `linha 6, coluna 38: caractere não reconhecido: ';'` |
| [texto_sem_fechar.ml](invalidos/texto_sem_fechar.ml) | léxica | `linha 6, coluna 17: texto sem fechar` |
| [numero_malformado.ml](invalidos/numero_malformado.ml) | léxica | `linha 7, coluna 30: número malformado: '.5'` |
| [expressao_operador_duplo.ml](invalidos/expressao_operador_duplo.ml) | sintática | `linha 3, coluna 40: '*' está sobrando aqui` |
| [parenteses_sem_fechar.ml](invalidos/parenteses_sem_fechar.ml) | sintática | `linha 3, coluna 20`: parêntese aberto sem fechar |
| [se_sem_condicao.ml](invalidos/se_sem_condicao.ml) | sintática | `linha 7, coluna 19: encontrei fim de linha` no lugar da condição |
| [operacao_sem_requer.ml](invalidos/operacao_sem_requer.ml) | sintática | `linha 6, coluna 17: encontrei 'narrar', mas esperava 'requer'` |
| [iniciar_fora_de_posicao.ml](invalidos/iniciar_fora_de_posicao.ml) | sintática | `linha 4, coluna 1`: declaração depois de `iniciar` |
| [tipo_incompativel_soma.ml](invalidos/tipo_incompativel_soma.ml) | semântica | `linha 7, coluna 41: tipos incompatíveis para operador '+': 'texto' e 'inteiro'` |
| [tipo_incompativel_atribuicao.ml](invalidos/tipo_incompativel_atribuicao.ml) | semântica | `linha 7, coluna 48: atribuição de tipo incompatível` |
| [variavel_nao_declarada.ml](invalidos/variavel_nao_declarada.ml) | semântica | `linha 12, coluna 24: caminho ou membro 'fantasma.mensagem' inexistente` |
| [metodo_receptor_invalido.ml](invalidos/metodo_receptor_invalido.ml) | semântica | `linha 7, coluna 9: receptor 'Campanha' não possui método de criação 'cenario'` |
| [operacao_sem_booleano_requer.ml](invalidos/operacao_sem_booleano_requer.ml) | semântica | `linha 10, coluna 24: cláusula 'requer' exige expressão do tipo 'booleano'` |
| [ciclo_dependencia_marcos.ml](invalidos/ciclo_dependencia_marcos.ml) | semântica | `linha 16, coluna 17: dependência cíclica detectada entre marcos: m1 -> m2 -> m1` |
| [historia_de_outra_campanha.ml](invalidos/historia_de_outra_campanha.ml) | semântica | `linha 11, coluna 1: história 'camp2.historias.h2' não pertence à campanha 'camp1'` |

Os nomes `ola`, `quadrado` e `espiral` são os pedidos no enunciado; o conteúdo foi
adaptado ao domínio de RPG.

## 3. Fase do projeto

- **E2 — Analisador Léxico:** especificação preenchida, gramática léxica ANTLR, motor de layout, listagem de tokens e diagnósticos entregues.
- **E3 — Analisador Sintático e Árvore:** gramática sintática `SuaLingParser.g4` (com `tokenVocab`), CLI `src/sintatico.py` com opção `--arvore`, precedência de operadores e 5 exemplos inválidos sintáticos entregues.
- **E4 — Análise Semântica e Execução:** sistema de tipos estático, tabela de símbolos hierárquica, verificação de escopo e receptores permitidos, validação de ciclos em grafos de marcos, interpretador/runtime com motor de sessão RPG (`src/interpretador.py`) e CLI de simulação (`src/executar.py`).

### Executando o Compilador e Interpretador (E4)

Para validar a semântica de um programa:
```bash
python src/executar.py --apenas-semantico exemplos/ola.ml
```

Para iniciar a simulação interativa da sessão de RPG:
```bash
python src/executar.py exemplos/ola.ml
```

Para executar comandos narrativos em lote via script:
```bash
python src/executar.py --script tests/roteiro_ola.txt exemplos/ola.ml
```

O analisador sintático valida a estrutura gramatical e constrói a árvore sintática concreta (Parse Tree). A árvore pode ser inspecionada executando:

```bash
python src/sintatico.py --arvore exemplos/ola.ml
```

## 4. Visualizador Interativo e Didático

O projeto inclui um painel web estático e offline para explorar visualmente as etapas do compilador de forma interativa e didática:

```bash
python src/visualizar.py exemplos/ola.ml
```

O comando compila o arquivo, gera um painel HTML em `visualizacoes/` (ou caminho especificado) e abre o navegador padrão automaticamente.

### Recursos do Visualizador:
- **Painel Léxico:** tabela de tokens identificados (linha, coluna, tipo e lexema), com destaque e sincronização com o código-fonte ao clicar ou passar o cursor.
- **Painel Sintático:** árvore sintática concreta (CST) interativa com nós expansíveis/recolhíveis, modo compacto (ocultando quebras de linha e indentação), diagrama hierárquico em SVG nativo e sincronização bidirecional com as linhas do código.
- **Painel da Narrativa:** extração estrutural das entidades de domínio declaradas (universos, personagens, histórias, capítulos, marcos) e visualização de fluxo com **grafo de dependência de marcos** em SVG, além das operações e ponto de partida da sessão de RPG.
- **Diagnósticos Amigáveis:** mensagens sintáticas traduzidas para português claro e parada preventiva caso existam erros léxicos.
- **100% Offline:** sem dependências de frameworks JS ou CDNs externas, funcionando em qualquer navegador moderno.

Opções disponíveis no CLI:
- `--saida <caminho>`: define o arquivo HTML de saída personalizado.
- `--nao-abrir`: gera o arquivo sem disparar o navegador automaticamente.

## 5. Como rodar os testes

Após instalar as dependências e gerar o lexer e parser (`sh gerar.sh` ou `.\gerar.ps1`):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Com o ambiente virtual ativo no Git Bash:

```sh
python -m unittest discover -s tests -v
```

Os 56 testes cobrem a análise léxica (25 testes), a análise sintática (8 testes), o pipeline de visualização/extração (15 testes), a análise semântica (5 testes) e a execução/runtime (3 testes), verificando reconhecimento de tokens, precedência de operadores na árvore, layout/indentação, detecção e recuperação de erros, tipagem estática, ciclos em grafos e simulação da narrativa de RPG, além de validar todos os programas de teste em `exemplos/` e `invalidos/`.


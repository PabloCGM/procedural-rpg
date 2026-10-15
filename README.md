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
.\.venv\Scripts\python.exe src/lexico.py exemplos/ola.ml
```

Em Linux/macOS ou terminal com `sh`, usando o ambiente virtual:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
sh gerar.sh
python src/lexico.py exemplos/ola.ml
```

`gerar.sh` fixa a versão do gerador e produz os arquivos em `gerado/`.
Há também `gerar.ps1` para PowerShell quando a execução de scripts estiver habilitada
e `antlr4` estiver no PATH; o comando direto acima funciona sem alterar essa política.
Na primeira geração, `antlr4-tools` pode baixar o JAR do ANTLR. Java não é necessário
para executar um lexer que já foi gerado.

Regere o lexer após modificar `gramatica/SuaLing.g4`. O arquivo contém somente regras
léxicas; não há parser. O gerador e o runtime são mantidos na mesma versão, conforme a
[documentação oficial do alvo Python do ANTLR](https://github.com/antlr/antlr4/blob/4.13.2/doc/python-target.md).
Arquivos gerados e o ambiente virtual são ignorados pelo Git.

O arquivo é declarado como `lexer grammar`. Com `grammar SuaLing;` e nenhuma regra de
parser, o ANTLR 4.13.2 falha na geração com `error(99): grammar SuaLing has no rules`.
Nessa mesma versão, `antlr4-parse` (seção 6.1 do enunciado) lança `ClassCastException`
ao receber uma gramática somente léxica. Por isso, a inspeção rápida dos tokens é feita
com `src/lexico.py`, que também mostra a coluna e os erros.

### Saída e erros

O programa lista o nome, lexema, linha e coluna de cada token e imprime o total.
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
| `0` | Nenhum erro léxico ou de indentação encontrado. |
| `1` | Erros de tokens ou indentação, com linha e coluna. |
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
do próprio arquivo:

| Arquivo | Erro apontado |
|---|---|
| [caractere_invalido.ml](invalidos/caractere_invalido.ml) | `linha 6, coluna 38: caractere não reconhecido: ';'` |
| [texto_sem_fechar.ml](invalidos/texto_sem_fechar.ml) | `linha 6, coluna 17: texto sem fechar` |
| [numero_malformado.ml](invalidos/numero_malformado.ml) | `linha 7, coluna 30: número malformado: '.5'` |

Os nomes `ola`, `quadrado` e `espiral` são os pedidos no enunciado; o conteúdo foi
adaptado ao domínio de RPG.

## 3. Fase do projeto

- **E2 — Analisador Léxico:** especificação preenchida, gramática léxica ANTLR, motor de layout, listagem de tokens e diagnósticos entregues.
- **E3 — Analisador Sintático e Árvore:** gramática sintática `SuaLingParser.g4` (com `tokenVocab`), CLI `src/sintatico.py` com opção `--arvore`, precedência de operadores e 5 exemplos inválidos sintáticos entregues.
- **E4:** análise semântica e execução não implementadas.

O analisador sintático valida a estrutura gramatical e constrói a árvore sintática concreta (Parse Tree). A árvore pode ser inspecionada executando:

```bash
python src/sintatico.py --arvore exemplos/ola.ml
```

## 4. Como rodar os testes

Após instalar as dependências e gerar o lexer e parser (`sh gerar.sh` ou `.\gerar.ps1`):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Com o ambiente virtual ativo no Git Bash:

```sh
python -m unittest discover -s tests -v
```

Os 33 testes cobrem a análise léxica (25 testes) e a análise sintática (8 testes), verificando reconhecimento de tokens, precedência de operadores na árvore, layout/indentação, detecção e recuperação de erros, além de validar todos os programas de teste em `exemplos/`, `invalidos/` e `invalidos_sintaticos/`.


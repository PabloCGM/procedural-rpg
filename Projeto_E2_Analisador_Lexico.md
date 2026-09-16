# Projeto do semestre
## Uma linguagem de programação

**Grupos de 3 a 4** - Linguagens Formais e Compiladores

Cada grupo projeta e implementa uma linguagem de programação pequena, percorrendo as três fases de um compilador. O trabalho é dividido em etapas ao longo do semestre.

| etapa | o que entrega | quando |
|---|---|---|
| E2 | especificação da linguagem e analisador léxico | encontro 8 |
| E3 | analisador sintático e árvore sintática | encontro 14 |
| E4 | análise semântica e execução | encontro 16 |

Este documento descreve a E2, que vale 1,5 ponto na Avaliação de Grau 1.

## 1 Escolha do domínio

A linguagem precisa servir para alguma coisa. Não vale uma linguagem genérica de propósito geral.

| domínio | o programa faz | tokens interessantes |
|---|---|---|
| desenho | move, gira, levanta a caneta | comandos, ângulos, cores |
| consulta de dados | filtra e agrupa registros | comparações, campos, condições, dispositivos |
| automação | liga a luz se o sensor passar de X | |
| jogo de tabuleiro | define regras e movimentos | coordenadas, peças |
| receita | ingredientes, passos, tempos | quantidades, unidades |
| música | notas, duração, repetições | notas, tempos, dinâmica |
| planilha | fórmulas sobre células | referências, funções, faixas |

Outros domínios são aceitos, mediante aprovação. Dois grupos não podem escolher o mesmo domínio, e a definição é por ordem de comunicação.

## 2 Parte A: Especificação da linguagem

Um arquivo `docs/especificacao.md` respondendo, nesta ordem:
1. Para que serve a linguagem, em duas frases.
2. Um programa de exemplo completo, comentado linha a linha.
3. Que tipos de dado existem.
4. Que comandos existem.
5. Que operadores existem, e com que precedência.
6. Como são os comentários.
7. Três coisas que a linguagem deliberadamente não faz.

O item 7 é o que separa projeto pensado de projeto improvisado. Toda linguagem boa recusa coisas de propósito, e saber o que ficou de fora é tão importante quanto saber o que entrou.

A especificação vem antes do código. Sem ela, o grupo descobre no meio do caminho que não concordava sobre o que estava construindo.

## 3 Parte B: O analisador léxico

Um arquivo `gramatica/SuaLing.g4` contendo apenas as regras de lexer as de nome em MAIÚSCULAS.

Precisa reconhecer, no mínimo:
* identificadores
* números inteiros e reais
* pelo menos um tipo de literal de texto
* as palavras-chave da sua linguagem
* os operadores
* comentários, descartados
* espaço em branco, descartado

### 3.1 Exemplo de referência

```antlr
grammar Calc;
//--- LEXER: MAIUSCULAS
COMANDO: mova | gire | levante;
IDENT: [a-zA-Z_] [a-zA-Z_0-9]*;
NUMERO: [0-9]+(.[0-9]+)?;
TEXTO: '"' ~[
]* '"';
COMENT: '//' ~[
]* -> skip;
ESPACO: [ 	
]+ -> skip;
```

### 3.2 O programa que lista os tokens

Um arquivo `src/lexico.py` que recebe o caminho de um programa e imprime os tokens reconhecidos:

```bash
$ python src/lexico.py exemplos/ola.ml
COMANDO mova linha 1
NUMERO 100 linha 1
PONTOVIRG linha 1
34 tokens reconhecidos
```

Ao encontrar um caractere que nenhuma regra reconhece, o programa deve apontar a linha e a coluna.

## 4 Parte C. Exemplos

Três programas válidos e três inválidos:

**Válidos:**
* `exemplos/ola.ml`
* `exemplos/quadrado.ml`
* `exemplos/espiral.ml`

**Inválidos:**
* `invalidos/caractere_invalido.ml`
* `invalidos/texto_sem_fechar.ml`
* `invalidos/numero_malformado.ml`

Cada arquivo inválido com nome indicando o problema, e o analisador deve localizar o erro.
Os exemplos inválidos valem tanto quanto os válidos. Eles são a prova de que o analisador detecta problemas, e não apenas de que aceita coisas certas.

## 5 O repositório

```text
minha-linguagem/
├── README.md
├── .gitignore           # gerado/, __pycache__/
├── gerar.sh             # regenera o codigo do ANTLR
├── gramatica/
│   └── SuaLing.g4
├── src/
│   └── lexico.py
├── exemplos/
└── docs/
    ├── especificacao.md
    └── DIARIO.md
```

### 5.1 O código gerado não vai para o Git

O ANTLR produz vários arquivos a partir do `g4`. Versioná-los polui o histórico e leva alguém a editar por engano um arquivo que será sobrescrito.

**# .gitignore**
```gitignore
gerado/
*.tokens
*.interp
__pycache__/
```

**# gerar.sh**
```bash
antlr4 -Dlanguage=Python3 -visitor -o gerado gramatica/SuaLing.g4
```

### 5.2 O README

Precisa responder, em ordem: que linguagem é essa com um exemplo, como instalar e rodar, em que fase o projeto está, e como rodar os testes.

### 5.3 O DIARIO.md

Uma entrada por sessão de trabalho, com data, o que foi tentado e o que aconteceu.

```markdown
## 12/09
Tentamos usar // para comentario, mas colide com o operador de divisao inteira que tinhamos definido. Trocamos o comentario para #.

## 15/09
O NUMERO estava engolindo o ponto final da instrucao. Era ambiguidade entre 3. e 3 seguido de ponto. Exigimos digito depois do ponto.
```

É pelo diário que se avalia o processo. Em projeto de linguagem as decisões são cheias de arrependimento: vocês vão escolher um símbolo e depois descobrir que ele conflita com outro. Registrar essa descoberta vale mais que o conserto.
Espera-se histórico de commits distribuído ao longo dos dias, não um único commit na véspera.

## 6 Instalando o ANTLR

O caminho mais simples exige apenas Python 3:

```bash
pip install antlr4-tools antlr4-python3-runtime
```

O comando cria os executáveis `antlr4` e `antlr4-parse`, que baixam e instalam o Java automaticamente na primeira execução. Ele pergunta se pode instalar; responda que sim.

### 6.1 Testando a gramática sem gerar código

O `antlr4-parse` mostra os tokens direto, e é a forma mais rápida de validar as regras de lexer:

```bash
antlr4-parse SuaLing.g4 programa -tokens
```

Use isso desde o primeiro dia, antes de escrever qualquer Python.

Instalem hoje. O ANTLR depende de Java e a primeira instalação costuma dar trabalho, especialmente no Windows. Avisem se travar, não deixem para a véspera da entrega.

### 6.2 Documentação

* Guia oficial de início: [https://github.com/antlr/antlr4/blob/master/doc/getting-started.md](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md)
* Documentação completa: [https://github.com/antlr/antlr4/tree/master/doc](https://github.com/antlr/antlr4/tree/master/doc)
* Tutorial extenso, com exemplos em Python: [https://tomassetti.me/antlr-mega-tutorial/](https://tomassetti.me/antlr-mega-tutorial/)
* Tutorial em português: [https://gabrielvaleze16.medium.com/tutorial-do-antlr-v4-cc4eb6d9c1ba](https://gabrielvaleze16.medium.com/tutorial-do-antlr-v4-cc4eb6d9c1ba)

Registrem no README a versão usada, porque código gerado por uma versão pode não rodar com o runtime de outra.

## 7 Avaliação

| critério | pontos |
|---|---|
| Especificação completa e coerente | 0,6 |
| Analisador léxico funcionando, com localização de erro | 0,6 |
| Exemplos válidos e inválidos | 0,3 |
| **total** | **1,5** |

**Descontos:** Repositório com commit único no dia da entrega, código gerado versionado, ou ausência do diário.

Não se avalia o tamanho da linguagem. Uma linguagem pequena, bem especificada e com o léxico correto vale mais que uma ambiciosa e incompleta.

## 8 Prazos

| o que | quando |
|---|---|
| Comunicar grupo, domínio e link do repositório | |
| Entrega da E2 | |

O repositório deve ser criado no início do trabalho, não no fim. É dele que sai o histórico.

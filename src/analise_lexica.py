"""Reconhecimento ANTLR, diagnósticos e layout; sem análise sintática/semântica."""

from dataclasses import dataclass
from itertools import groupby

from antlr4 import InputStream, Token
from antlr4.error.ErrorListener import ErrorListener
from antlr4.Token import CommonToken

from gerado.SuaLing import SuaLing


@dataclass(frozen=True)
class Diagnostico:
    categoria: str
    linha: int
    coluna: int
    mensagem: str


@dataclass
class Resultado:
    tokens: list[Token]
    erros: list[Diagnostico]


def nome_token(token):
    return SuaLing.symbolicNames[token.type]


class _ErrosANTLR(ErrorListener):
    def __init__(self, erros):
        self.erros = erros

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.erros.append(Diagnostico("léxico", line, column + 1, msg))


def _erro_token(token):
    """Retorna um diagnóstico para tokens inválidos reconhecidos pela gramática."""
    mensagens = {
        SuaLing.NUMERO_MALFORMADO: f"número malformado: {token.text!r}",
        SuaLing.TABULACAO: "tabulação fora de texto/comentário; use espaços",
        SuaLing.CARACTERE_INVALIDO: f"caractere não reconhecido: {token.text!r}",
    }
    if token.type in mensagens:
        return Diagnostico("léxico", token.line, token.column + 1, mensagens[token.type])
    if token.type != SuaLing.TEXTO_INVALIDO:
        return None

    # Localiza o escape incorreto, sem confundir uma aspa escapada com fechamento.
    i = 1
    while i < len(token.text):
        if token.text[i] == "\\":
            if i + 1 < len(token.text) and token.text[i + 1] not in '"\\nt':
                return Diagnostico(
                    "léxico", token.line, token.column + i + 1,
                    f"escape inválido: {token.text[i:i + 2]!r}",
                )
            i += 2
        else:
            i += 1
    return Diagnostico("léxico", token.line, token.column + 1, "texto sem fechar")


def _sintetico(tipo, texto, linha, coluna, inicio):
    token = CommonToken(type=tipo, start=inicio, stop=inicio - 1)
    token.text = texto
    token.line = linha
    token.column = coluna
    return token


def analisar(texto):
    # Uniformiza terminadores sem alterar as colunas ou o conteúdo dos literais válidos.
    texto = texto.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    erros = []
    lexer = SuaLing(InputStream(texto))
    lexer.removeErrorListeners()
    lexer.addErrorListener(_ErrosANTLR(erros))
    brutos = lexer.getAllTokens()
    eof = lexer.nextToken()
    linhas = texto.split("\n")
    inicios = [0]
    for linha in linhas[:-1]:
        inicios.append(inicios[-1] + len(linha) + 1)

    tokens = []
    niveis = [0]
    primeira = True
    # Comentários e espaços já foram descartados, mas ANTLR preserva linha/coluna.
    for numero, grupo in groupby(brutos, key=lambda token: token.line):
        grupo = list(grupo)
        primeiro = grupo[0]
        recuo = primeiro.column
        mensagem = None
        if primeira and recuo != 0:
            mensagem = "a primeira instrução deve começar na coluna 1"
        elif recuo % 4:
            mensagem = "a indentação deve usar múltiplos de quatro espaços"
        elif recuo > niveis[-1] + 4:
            mensagem = "um novo nível deve acrescentar exatamente quatro espaços"

        if mensagem:
            erros.append(Diagnostico("de indentação", numero, recuo + 1, mensagem))
        elif recuo > niveis[-1]:
            niveis.append(recuo)
            tokens.append(_sintetico(SuaLing.INDENTA, "<INDENTA>", numero, recuo, primeiro.start))
        else:
            while recuo < niveis[-1]:
                niveis.pop()
                tokens.append(_sintetico(SuaLing.DEDENTA, "<DEDENTA>", numero, recuo, primeiro.start))
        primeira = False

        for token in grupo:
            erro = _erro_token(token)
            if erro is None:
                tokens.append(token)
            else:
                erros.append(erro)

        fim = len(linhas[numero - 1])
        tokens.append(_sintetico(SuaLing.NOVA_LINHA, "\n", numero, fim, inicios[numero - 1] + fim))

    while len(niveis) > 1:
        niveis.pop()
        tokens.append(_sintetico(SuaLing.DEDENTA, "<DEDENTA>", eof.line, eof.column, eof.start))
    erros.sort(key=lambda erro: (erro.linha, erro.coluna))
    return Resultado(tokens, erros)

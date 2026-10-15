"""Análise sintática do Procedural RPG usando ANTLR 4 (E3)."""

from dataclasses import dataclass
from typing import Any

from antlr4 import CommonTokenStream, Token
from antlr4.error.ErrorListener import ErrorListener
from antlr4.ListTokenSource import ListTokenSource
from antlr4.Token import CommonToken

from gerado.SuaLingParser import SuaLingParser
from src.analise_lexica import Diagnostico, analisar as analisar_lexico


@dataclass
class ResultadoSintatico:
    arvore: Any
    erros: list[Diagnostico]
    parser: SuaLingParser


class _ErrosSintaticosANTLR(ErrorListener):
    def __init__(self, erros: list[Diagnostico]):
        self.erros = erros

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        coluna = (column + 1) if column is not None else 1
        self.erros.append(Diagnostico("sintático", line, coluna, msg))


def formatar_arvore(node, parser, recuo=0) -> str:
    """Gera uma representação textual identada e legível da árvore sintática."""
    if hasattr(node, "getSymbol"):
        simbolo = node.getSymbol()
        return "  " * recuo + f"{simbolo.text!r}"

    nome = type(node).__name__.removesuffix("Context")
    linhas = ["  " * recuo + nome]
    if hasattr(node, "children") and node.children:
        for filho in node.children:
            linhas.append(formatar_arvore(filho, parser, recuo + 1))
    return "\n".join(linhas)


def analisar_sintaxe(texto: str) -> ResultadoSintatico:
    resultado_lexico = analisar_lexico(texto)
    erros = list(resultado_lexico.erros)

    eof = CommonToken(type=Token.EOF)
    eof.text = "<EOF>"
    eof.line = resultado_lexico.tokens[-1].line if resultado_lexico.tokens else 1
    eof.column = resultado_lexico.tokens[-1].column if resultado_lexico.tokens else 0

    tokens_com_eof = resultado_lexico.tokens + [eof]
    stream = CommonTokenStream(ListTokenSource(tokens_com_eof))

    parser = SuaLingParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(_ErrosSintaticosANTLR(erros))

    arvore = parser.programa()
    erros.sort(key=lambda erro: (erro.linha, erro.coluna))
    return ResultadoSintatico(arvore=arvore, erros=erros, parser=parser)

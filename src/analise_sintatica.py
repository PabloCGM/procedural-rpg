"""Análise sintática do Procedural RPG usando ANTLR 4 (E3)."""

from dataclasses import dataclass
from typing import Any

from antlr4 import CommonTokenStream, Token
from antlr4.error.ErrorListener import ErrorListener
from antlr4.ListTokenSource import ListTokenSource
from antlr4.Token import CommonToken

from gerado.SuaLingParser import SuaLingParser
from src.analise_lexica import Diagnostico, Resultado as ResultadoLexico, analisar as analisar_lexico
from src.visualizacao.mensagens import traduzir_mensagem_antlr


@dataclass
class ResultadoSintatico:
    arvore: Any
    erros: list[Diagnostico]
    parser: SuaLingParser | None
    lexico: ResultadoLexico | None = None
    bloqueado: bool = False


class _ErrosSintaticosANTLR(ErrorListener):
    def __init__(self, erros: list[Diagnostico]):
        self.erros = erros

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        coluna = (column + 1) if column is not None else 1
        msg_traduzida, _ = traduzir_mensagem_antlr(msg)
        self.erros.append(Diagnostico("sintático", line, coluna, msg_traduzida))


def formatar_arvore(node, parser, recuo=0) -> str:
    """Gera uma representação textual identada e legível da árvore sintática."""
    if node is None:
        return ""
    if hasattr(node, "getSymbol"):
        simbolo = node.getSymbol()
        return "  " * recuo + f"{simbolo.text!r}"

    nome = type(node).__name__.removesuffix("Context")
    linhas = ["  " * recuo + nome]
    if hasattr(node, "children") and node.children:
        for filho in node.children:
            linhas.append(formatar_arvore(filho, parser, recuo + 1))
    return "\n".join(linhas)


def analisar_tokens(tokens: list[Token], erros_iniciais: list[Diagnostico] | None = None) -> tuple[Any, SuaLingParser, list[Diagnostico]]:
    """Executa o parser sobre uma lista de tokens já gerada."""
    erros = list(erros_iniciais or [])
    eof = CommonToken(type=Token.EOF)
    eof.text = "<EOF>"
    eof.line = tokens[-1].line if tokens else 1
    eof.column = tokens[-1].column if tokens else 0

    tokens_com_eof = tokens + [eof]
    stream = CommonTokenStream(ListTokenSource(tokens_com_eof))

    parser = SuaLingParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(_ErrosSintaticosANTLR(erros))

    arvore = parser.programa()
    erros.sort(key=lambda erro: (erro.linha, erro.coluna))
    return arvore, parser, erros


def analisar_sintaxe(texto: str, parar_em_erro_lexico: bool = True) -> ResultadoSintatico:
    """Executa o pipeline completo (léxico + sintático), com parada preventiva em erros léxicos."""
    resultado_lexico = analisar_lexico(texto)
    erros = list(resultado_lexico.erros)

    if resultado_lexico.erros and parar_em_erro_lexico:
        return ResultadoSintatico(
            arvore=None,
            erros=erros,
            parser=None,
            lexico=resultado_lexico,
            bloqueado=True,
        )

    arvore, parser, todos_erros = analisar_tokens(resultado_lexico.tokens, erros)
    return ResultadoSintatico(
        arvore=arvore,
        erros=todos_erros,
        parser=parser,
        lexico=resultado_lexico,
        bloqueado=False,
    )

"""Lista os tokens da linguagem Procedural RPG (Parte B da E2)."""

import argparse
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analisa tokens e indentação; não executa a campanha."
    )
    parser.add_argument("programa", type=Path, help="arquivo-fonte em UTF-8")
    args = parser.parse_args(argv)

    raiz = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(raiz))
    try:
        from src.analise_lexica import analisar, nome_token
    except ModuleNotFoundError as exc:
        if exc.name == "antlr4":
            mensagem = "Instale as dependências: python -m pip install -r requirements.txt"
        elif exc.name in {"gerado", "gerado.SuaLing"}:
            mensagem = "Gere o lexer primeiro: ./gerar.ps1 (PowerShell) ou sh gerar.sh"
        else:
            raise
        print(f"Erro de preparação: {mensagem}", file=sys.stderr)
        return 2

    try:
        # utf-8-sig aceita também arquivos com BOM criados por editores do Windows.
        texto = args.programa.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"Erro ao ler {args.programa}: {exc}", file=sys.stderr)
        return 2

    resultado = analisar(texto)
    for token in resultado.tokens:
        print(
            f"{nome_token(token)} {token.text!r} "
            f"linha {token.line} coluna {token.column + 1}"
        )
    print(f"{len(resultado.tokens)} tokens reconhecidos")
    for erro in resultado.erros:
        print(
            f"Erro {erro.categoria}: linha {erro.linha}, coluna {erro.coluna}: "
            f"{erro.mensagem}",
            file=sys.stderr,
        )
    if resultado.erros:
        print(f"{len(resultado.erros)} erro(s) encontrado(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    for saida in (sys.stdout, sys.stderr):
        if hasattr(saida, "reconfigure"):
            saida.reconfigure(encoding="utf-8")
    raise SystemExit(main())

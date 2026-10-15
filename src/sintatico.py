"""Analisador sintático da linguagem Procedural RPG (Etapa E3)."""

import argparse
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analisa a sintaxe e constrói a árvore sintática (E3)."
    )
    parser.add_argument("programa", type=Path, help="arquivo-fonte em UTF-8 (.ml)")
    parser.add_argument(
        "--arvore",
        action="store_true",
        help="imprime a árvore sintática concreta gerada",
    )
    args = parser.parse_args(argv)

    raiz = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(raiz))

    try:
        from src.analise_sintatica import analisar_sintaxe, formatar_arvore
    except ModuleNotFoundError as exc:
        if exc.name == "antlr4":
            mensagem = "Instale as dependências: python -m pip install -r requirements.txt"
        elif exc.name in {"gerado", "gerado.SuaLingParser"}:
            mensagem = "Gere os arquivos ANTLR: sh gerar.sh ou ./gerar.ps1"
        else:
            raise
        print(f"Erro de preparação: {mensagem}", file=sys.stderr)
        return 2

    try:
        texto = args.programa.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"Erro ao ler {args.programa}: {exc}", file=sys.stderr)
        return 2

    resultado = analisar_sintaxe(texto)

    for erro in resultado.erros:
        print(
            f"Erro {erro.categoria}: linha {erro.linha}, coluna {erro.coluna}: "
            f"{erro.mensagem}",
            file=sys.stderr,
        )

    if resultado.erros:
        print(f"{len(resultado.erros)} erro(s) encontrado(s)", file=sys.stderr)
        return 1

    print(f"Sucesso sintático: {args.programa} é válido!")
    if args.arvore:
        print("\n--- ÁRVORE SINTÁTICA CONCRETA ---")
        print(formatar_arvore(resultado.arvore, resultado.parser))

    return 0


if __name__ == "__main__":
    for saida in (sys.stdout, sys.stderr):
        if hasattr(saida, "reconfigure"):
            saida.reconfigure(encoding="utf-8")
    raise SystemExit(main())

"""CLI para executar o pipeline do compilador e abrir o visualizador interativo em HTML."""

import argparse
from pathlib import Path
import sys
import webbrowser


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Executa o compilador Procedural RPG e abre o visualizador web interativo."
    )
    parser.add_argument("programa", type=Path, help="arquivo-fonte em UTF-8 (.ml)")
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="caminho do arquivo HTML de saída (padrão: visualizacoes/<nome>.html)",
    )
    parser.add_argument(
        "--nao-abrir",
        action="store_true",
        help="não abre o navegador automaticamente após gerar",
    )
    args = parser.parse_args(argv)

    raiz = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(raiz))

    try:
        from src.analise_sintatica import analisar_sintaxe
        from src.visualizacao.estrutura import extrair_estrutura_narrativa
        from src.visualizacao.modelo import construir_modelo_dados
        from src.visualizacao.html import salvar_visualizacao_html
    except ModuleNotFoundError as exc:
        print(f"Erro de preparação de módulos: {exc}", file=sys.stderr)
        return 2

    if not args.programa.exists():
        print(f"Arquivo não encontrado: {args.programa}", file=sys.stderr)
        return 2

    try:
        texto = args.programa.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"Erro ao ler {args.programa}: {exc}", file=sys.stderr)
        return 2

    # Executa o pipeline com parada preventiva se houver erro léxico
    resultado_sintatico = analisar_sintaxe(texto, parar_em_erro_lexico=True)

    # Extração estrutural se a árvore foi construída
    estrutura = extrair_estrutura_narrativa(resultado_sintatico.arvore, texto) if resultado_sintatico.arvore else {}

    # Constrói o modelo de dados completo
    modelo = construir_modelo_dados(
        caminho_arquivo=str(args.programa),
        texto_fonte=texto,
        resultado_sintatico=resultado_sintatico,
        estrutura=estrutura,
    )

    # Define caminho de saída
    if args.saida:
        caminho_saida = args.saida
    else:
        caminho_saida = raiz / "visualizacoes" / f"{args.programa.stem}.html"

    salvar_visualizacao_html(modelo, caminho_saida)

    # Se não foi solicitada a supressão, abre no navegador padrão
    if not args.nao_abrir:
        try:
            webbrowser.open(caminho_saida.resolve().as_uri())
        except Exception as exc:
            print(f"Não foi possível abrir o navegador automaticamente: {exc}", file=sys.stderr)

    if resultado_sintatico.erros:
        print(f"Visualizador gerado com {len(resultado_sintatico.erros)} erro(s) em: {caminho_saida}", file=sys.stderr)
        for erro in resultado_sintatico.erros:
            print(f"  • Linha {erro.linha}, coluna {erro.coluna}: {erro.mensagem}", file=sys.stderr)
        return 1

    print(f"Visualizador gerado com sucesso em: {caminho_saida}")
    return 0


if __name__ == "__main__":
    for saida in (sys.stdout, sys.stderr):
        if hasattr(saida, "reconfigure"):
            saida.reconfigure(encoding="utf-8")
    raise SystemExit(main())

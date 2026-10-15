"""Gerador do arquivo HTML autocontido e offline para visualização do compilador."""

import json
from pathlib import Path
from typing import Any

DIRETORIO_ASSETS = Path(__file__).parent / "assets"


def gerar_html_visualizador(modelo_dados: dict[str, Any]) -> str:
    """Lê os assets e embute CSS, JS e dados JSON em uma única página HTML autônoma."""
    template_path = DIRETORIO_ASSETS / "template.html"
    css_path = DIRETORIO_ASSETS / "estilo.css"
    js_path = DIRETORIO_ASSETS / "app.js"

    template = template_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")

    # Serialização segura contra injeção de tags em literais de código
    json_dados = json.dumps(modelo_dados, ensure_ascii=False, indent=2).replace("<", "\\u003c")

    html = template.replace("__CSS__", css)
    html = html.replace("__JS__", js)
    html = html.replace("__DADOS_JSON__", json_dados)

    return html


def salvar_visualizacao_html(modelo_dados: dict[str, Any], caminho_saida: Path) -> Path:
    """Gera e salva o arquivo HTML no caminho especificado."""
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    html = gerar_html_visualizador(modelo_dados)
    caminho_saida.write_text(html, encoding="utf-8")
    return caminho_saida

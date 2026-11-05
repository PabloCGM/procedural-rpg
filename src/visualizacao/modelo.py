"""Serialização e estruturação do modelo de dados do compilador para visualização."""

from typing import Any
from antlr4.tree.Tree import TerminalNodeImpl, ErrorNodeImpl

from gerado.SuaLing import SuaLing
from src.analise_lexica import Token, nome_token
from src.analise_sintatica import ResultadoSintatico


CATEGORIAS_TOKEN = {
    # Palavras reservadas de controle e declaração
    "CONCLUIR": "palavra_chave",
    "QUANDO": "palavra_chave",
    "ENCERRAR": "palavra_chave",
    "OPERACAO": "palavra_chave",
    "REQUER": "palavra_chave",
    "INICIAR": "palavra_chave",
    "COM": "palavra_chave",
    "NARRAR": "palavra_chave",
    "SE": "palavra_chave",
    "SENAO": "palavra_chave",
    "E": "palavra_chave",
    "OU": "palavra_chave",
    "NAO": "palavra_chave",

    # Tipos
    "TIPO_INTEIRO": "tipo",
    "TIPO_REAL": "tipo",
    "TIPO_TEXTO": "tipo",
    "TIPO_BOOLEANO": "tipo",

    # Literais
    "INTEIRO": "literal",
    "REAL": "literal",
    "TEXTO": "literal",
    "VERDADEIRO": "literal",
    "FALSO": "literal",

    # Identificadores
    "IDENT": "identificador",

    # Operadores
    "IGUAL": "operador",
    "DIFERENTE": "operador",
    "MENOR_IGUAL": "operador",
    "MAIOR_IGUAL": "operador",
    "ATRIBUICAO": "operador",
    "MENOR": "operador",
    "MAIOR": "operador",
    "MAIS": "operador",
    "MENOS": "operador",
    "MULTIPLICACAO": "operador",
    "DIVISAO": "operador",
    "PONTO": "operador",

    # Delimitadores
    "ABRE_PAREN": "delimitador",
    "FECHA_PAREN": "delimitador",
    "VIRGULA": "delimitador",

    # Layout
    "INDENTA": "layout",
    "DEDENTA": "layout",
    "NOVA_LINHA": "layout",

    # Erros léxicos
    "NUMERO_MALFORMADO": "erro",
    "TEXTO_INVALIDO": "erro",
    "TABULACAO": "erro",
    "CARACTERE_INVALIDO": "erro",
}


def categorizar_token(tipo_str: str) -> str:
    """Retorna a categoria semântica do token para coloração."""
    return CATEGORIAS_TOKEN.get(tipo_str, "outro")


def serializar_tokens(tokens: list[Token]) -> list[dict[str, Any]]:
    """Converte lista de tokens em dicionários serializáveis."""
    lista = []
    for i, t in enumerate(tokens):
        nome = nome_token(t)
        sintetico = nome in {"INDENTA", "DEDENTA", "NOVA_LINHA"}
        tam = len(t.text) if t.text else 1
        col_fim = t.column + tam
        lista.append({
            "i": i,
            "tipo": nome,
            "categoria": categorizar_token(nome),
            "texto": t.text,
            "linha": t.line,
            "coluna": t.column + 1,
            "coluna_fim": col_fim + 1,
            "sintetico": sintetico,
        })
    return lista


def serializar_arvore(node: Any, contador: list[int] | None = None) -> dict[str, Any] | None:
    """Converte a Parse Tree do ANTLR em uma árvore JSON com intervalos de código."""
    if node is None:
        return None
    if contador is None:
        contador = [0]

    nodo_id = contador[0]
    contador[0] += 1

    # Folha de erro
    if isinstance(node, ErrorNodeImpl):
        sym = node.getSymbol()
        return {
            "id": nodo_id,
            "tipo": "erro",
            "nome": "ErroSintatico",
            "rotulo": None,
            "texto": sym.text if sym else "",
            "linha_inicio": sym.line if sym else 1,
            "coluna_inicio": (sym.column + 1) if sym else 1,
            "linha_fim": sym.line if sym else 1,
            "coluna_fim": (sym.column + len(sym.text) + 1) if sym and sym.text else 1,
            "filhos": [],
        }

    # Folha de token terminal
    if isinstance(node, TerminalNodeImpl):
        sym = node.getSymbol()
        texto = sym.text if sym else ""
        if sym and sym.type == Token.EOF:
            return None
        return {
            "id": nodo_id,
            "tipo": "token",
            "nome": SuaLing.symbolicNames[sym.type] if (sym and sym.type < len(SuaLing.symbolicNames)) else "TOKEN",
            "rotulo": None,
            "texto": texto,
            "linha_inicio": sym.line if sym else 1,
            "coluna_inicio": (sym.column + 1) if sym else 1,
            "linha_fim": sym.line if sym else 1,
            "coluna_fim": (sym.column + len(texto) + 1) if sym else 1,
            "filhos": [],
        }

    # Nó de regra
    classe_nome = type(node).__name__
    nome_regra = classe_nome.removesuffix("Context")
    rotulo = None

    # Se tiver classe especializada gerada por rótulo (ex: ExprMultiplicativaContext)
    if nome_regra.startswith("Expr") and nome_regra != "Expr":
        rotulo = nome_regra
        nome_regra = "expr"
    else:
        nome_regra = nome_regra.lower()

    filhos = []
    if hasattr(node, "children") and node.children:
        for filho in node.children:
            d_filho = serializar_arvore(filho, contador)
            if d_filho is not None:
                filhos.append(d_filho)

    # Calcula limites a partir dos tokens reais
    start_tok = getattr(node, "start", None)
    stop_tok = getattr(node, "stop", None)

    l_ini = start_tok.line if start_tok else 1
    c_ini = (start_tok.column + 1) if start_tok else 1
    l_fim = stop_tok.line if stop_tok else l_ini
    c_fim = (stop_tok.column + len(stop_tok.text) + 1) if stop_tok and stop_tok.text else c_ini

    return {
        "id": nodo_id,
        "tipo": "regra",
        "nome": nome_regra,
        "rotulo": rotulo,
        "texto": None,
        "linha_inicio": l_ini,
        "coluna_inicio": c_ini,
        "linha_fim": l_fim,
        "coluna_fim": c_fim,
        "filhos": filhos,
    }


def construir_modelo_dados(
    caminho_arquivo: str,
    texto_fonte: str,
    resultado_sintatico: ResultadoSintatico,
    estrutura: dict[str, Any] | None = None,
    resultado_semantico: Any = None,
) -> dict[str, Any]:
    """Gera o dicionário completo que alimenta a interface gráfica."""
    # Normaliza quebras de linha
    fonte_norm = texto_fonte.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")

    erros_lexicos = [e for e in resultado_sintatico.erros if e.categoria == "léxico" or "indentação" in e.categoria]
    erros_sintaticos = [e for e in resultado_sintatico.erros if e.categoria == "sintático"]
    erros_semanticos = resultado_semantico.erros if resultado_semantico else []

    status_lexico = "erro" if erros_lexicos else "ok"
    if resultado_sintatico.bloqueado:
        status_sintatico = "bloqueada"
        resumo_sintatico = "bloqueado por erro léxico"
    elif erros_sintaticos:
        status_sintatico = "erro"
        resumo_sintatico = f"{len(erros_sintaticos)} erro(s)"
    else:
        status_sintatico = "ok"
        resumo_sintatico = "árvore construída"

    status_narrativa = "bloqueada" if (resultado_sintatico.bloqueado or erros_sintaticos or resultado_sintatico.arvore is None) else "ok"

    if resultado_semantico is not None:
        if resultado_semantico.sucesso:
            status_semantico = "ok"
            resumo_semantico = f"{len(resultado_semantico.tabela.variaveis)} símbolos validados"
        else:
            status_semantico = "erro"
            resumo_semantico = f"{len(resultado_semantico.erros)} erro(s) semântico(s)"
    else:
        status_semantico = "bloqueada"
        resumo_semantico = "requer sintaxe válida"

    fases = [
        {
            "id": "lexico",
            "nome": "1. Análise Léxica",
            "status": status_lexico,
            "resumo": f"{len(resultado_sintatico.lexico.tokens)} tokens" if resultado_sintatico.lexico else "concluída",
        },
        {
            "id": "sintatico",
            "nome": "2. Análise Sintática",
            "status": status_sintatico,
            "resumo": resumo_sintatico,
        },
        {
            "id": "narrativa",
            "nome": "3. Estrutura Narrativa",
            "status": status_narrativa,
            "resumo": "entidades e marcos" if status_narrativa == "ok" else "requer sintaxe válida",
        },
        {
            "id": "semantico",
            "nome": "4. Análise Semântica (E4)",
            "status": status_semantico,
            "resumo": resumo_semantico,
        },
    ]

    tokens_serializados = serializar_tokens(resultado_sintatico.lexico.tokens) if resultado_sintatico.lexico else []
    arvore_serializada = serializar_arvore(resultado_sintatico.arvore) if resultado_sintatico.arvore else None

    todos_erros = list(resultado_sintatico.erros)
    if resultado_semantico:
        todos_erros.extend(resultado_semantico.erros)

    erros_serializados = [
        {
            "fase": e.categoria,
            "linha": e.linha,
            "coluna": e.coluna,
            "mensagem": e.mensagem,
        }
        for e in todos_erros
    ]

    semantico_serializado = {}
    if resultado_semantico and resultado_semantico.tabela:
        tab = resultado_semantico.tabela
        vars_list = []
        for nome, ent in tab.variaveis.items():
            campos_est = [{"campo": c.nome, "tipo": c.tipo.value} for c in ent.estado.values()]
            campos_fich = [{"campo": c.nome, "tipo": c.tipo.value} for c in ent.ficha.values()]
            vars_list.append({
                "variavel": nome,
                "tipo": ent.tipo.value if hasattr(ent.tipo, "value") else str(ent.tipo),
                "id": ent.id_instancia,
                "pai": ent.pai_variavel,
                "estado": campos_est,
                "ficha": campos_fich,
            })
        marcos_list = []
        for id_m, m in tab.marcos.items():
            marcos_list.append({
                "id": m.id_marco,
                "variavel": m.nome_variavel,
                "historia": m.historia_pai,
                "dependencias": m.dependencias,
            })
        ops_list = []
        for c_op, op in tab.operacoes.items():
            ops_list.append({
                "caminho": op.caminho,
                "id": op.id_operacao,
                "historia": op.historia_pai,
            })

        semantico_serializado = {
            "sucesso": resultado_semantico.sucesso,
            "campanha_iniciar": resultado_semantico.campanha_iniciar,
            "historia_iniciar": resultado_semantico.historia_iniciar,
            "variaveis": vars_list,
            "marcos": marcos_list,
            "operacoes": ops_list,
        }

    return {
        "arquivo": caminho_arquivo,
        "fonte": fonte_norm,
        "fases": fases,
        "tokens": tokens_serializados,
        "erros": erros_serializados,
        "arvore": arvore_serializada,
        "estrutura": estrutura or {},
        "semantico": semantico_serializado,
    }

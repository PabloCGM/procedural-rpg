"""Tradução e formatação amigável das mensagens de erro do ANTLR 4."""

import re

NOMES_TOKENS_PT = {
    r"'\n'": "fim de linha",
    "NOVA_LINHA": "fim de linha",
    "<EOF>": "fim do arquivo",
    "EOF": "fim do arquivo",
    "IDENT": "identificador",
    "TEXTO": "literal de texto",
    "INTEIRO": "número inteiro",
    "REAL": "número real",
    "INDENTA": "início de bloco (recuo de 4 espaços)",
    "DEDENTA": "fechamento de bloco",
    "TIPO_INTEIRO": "'inteiro'",
    "TIPO_REAL": "'real'",
    "TIPO_TEXTO": "'texto'",
    "TIPO_BOOLEANO": "'booleano'",
    "VERDADEIRO": "'verdadeiro'",
    "FALSO": "'falso'",
    "CONCLUIR": "'concluir'",
    "QUANDO": "'quando'",
    "ENCERRAR": "'encerrar'",
    "OPERACAO": "'operacao'",
    "REQUER": "'requer'",
    "INICIAR": "'iniciar'",
    "COM": "'com'",
    "NARRAR": "'narrar'",
    "SE": "'se'",
    "SENAO": "'senao'",
    "E": "'e'",
    "OU": "'ou'",
    "NAO": "'nao'",
    "IGUAL": "'=='",
    "DIFERENTE": "'!='",
    "MENOR_IGUAL": "'<='",
    "MAIOR_IGUAL": "'>='",
    "ATRIBUICAO": "'='",
    "MENOR": "'<'",
    "MAIOR": "'>'",
    "MAIS": "'+'",
    "MENOS": "'-'",
    "MULTIPLICACAO": "'*'",
    "DIVISAO": "'/'",
    "PONTO": "'.'",
    "ABRE_PAREN": "'('",
    "FECHA_PAREN": "')'",
    "VIRGULA": "','",
}


def _traduzir_esperado(esperado_str: str) -> str:
    """Traduz o conjunto de tokens esperados para uma lista legível."""
    esperado_str = esperado_str.strip()
    if esperado_str.startswith("{") and esperado_str.endswith("}"):
        itens_brutos = [item.strip() for item in esperado_str[1:-1].split(",") if item.strip()]
        itens_traduzidos = []
        for item in itens_brutos:
            item_limpo = item.strip("'")
            nome = NOMES_TOKENS_PT.get(item, NOMES_TOKENS_PT.get(item_limpo, item))
            if nome not in itens_traduzidos:
                itens_traduzidos.append(nome)
        if len(itens_traduzidos) == 1:
            return itens_traduzidos[0]
        if len(itens_traduzidos) <= 4:
            return ", ".join(itens_traduzidos[:-1]) + " ou " + itens_traduzidos[-1]
        return f"{', '.join(itens_traduzidos[:3])} ou outros ({len(itens_traduzidos)} alternativas válidas)"
    
    item_limpo = esperado_str.strip("'")
    return NOMES_TOKENS_PT.get(esperado_str, NOMES_TOKENS_PT.get(item_limpo, esperado_str))


def _traduzir_simbolo(simbolo_str: str) -> str:
    """Traduz um símbolo encontrado."""
    simbolo_str = simbolo_str.strip()
    return NOMES_TOKENS_PT.get(simbolo_str, simbolo_str)


def traduzir_mensagem_antlr(msg: str) -> tuple[str, str]:
    """
    Traduz uma mensagem técnica do ANTLR 4 para português amigável.
    Retorna uma tupla (mensagem_traduzida, mensagem_original).
    """
    msg_orig = msg

    # Caso 1: extraneous input 'X' expecting Y
    padrao_extraneous = re.match(r"^extraneous input (.+?) expecting (.+)$", msg)
    if padrao_extraneous:
        encontrado = _traduzir_simbolo(padrao_extraneous.group(1))
        esperado = _traduzir_esperado(padrao_extraneous.group(2))
        return f"{encontrado} está sobrando aqui; esperava {esperado}", msg_orig

    # Caso 2: mismatched input 'X' expecting Y
    padrao_mismatched = re.match(r"^mismatched input (.+?) expecting (.+)$", msg)
    if padrao_mismatched:
        encontrado = _traduzir_simbolo(padrao_mismatched.group(1))
        esperado = _traduzir_esperado(padrao_mismatched.group(2))
        return f"encontrei {encontrado}, mas esperava {esperado}", msg_orig

    # Caso 3: missing X at Y
    padrao_missing = re.match(r"^missing (.+?) at (.+)$", msg)
    if padrao_missing:
        faltou = _traduzir_esperado(padrao_missing.group(1))
        onde = _traduzir_simbolo(padrao_missing.group(2))
        return f"faltou {faltou} antes de {onde}", msg_orig

    # Caso 4: no viable alternative at input X
    padrao_no_viable = re.match(r"^no viable alternative at input (.+)$", msg)
    if padrao_no_viable:
        trecho = _traduzir_simbolo(padrao_no_viable.group(1))
        return f"não reconheci nenhuma construção gramatical válida em {trecho}", msg_orig

    return msg, msg_orig

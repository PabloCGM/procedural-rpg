"""Sistema de tipos da linguagem Procedural RPG (E4)."""

from enum import Enum, auto


class TipoPrimitivo(Enum):
    INTEIRO = "inteiro"
    REAL = "real"
    TEXTO = "texto"
    BOOLEANO = "booleano"
    NULO = "nulo"
    DESCONHECIDO = "desconhecido"


class TipoEntidade(Enum):
    UNIVERSO = "Universo"
    CAMPANHA = "Campanha"
    CENARIO = "Cenario"
    PERSONAGEM = "Personagem"
    HISTORIA = "Historia"
    CAPITULO = "Capitulo"
    MARCO = "Marco"
    CENA = "Cena"
    ITEM = "Item"
    INVENTARIO = "Inventario"
    COLECAO = "Colecao"
    OPERACAO = "Operacao"
    DESCONHECIDO = "Desconhecido"


def eh_numerico(tipo: TipoPrimitivo | str) -> bool:
    if isinstance(tipo, str):
        return tipo in ("inteiro", "real")
    return tipo in (TipoPrimitivo.INTEIRO, TipoPrimitivo.REAL)


def promover_aritmetica(t1: TipoPrimitivo, t2: TipoPrimitivo) -> TipoPrimitivo:
    """Aplica regras de promoção aritmética:
    - inteiro + inteiro -> inteiro
    - inteiro + real ou real + inteiro ou real + real -> real
    - Qualquer outro caso -> DESCONHECIDO (erro)
    """
    if t1 == TipoPrimitivo.INTEIRO and t2 == TipoPrimitivo.INTEIRO:
        return TipoPrimitivo.INTEIRO
    if (t1 == TipoPrimitivo.INTEIRO and t2 == TipoPrimitivo.REAL) or \
       (t1 == TipoPrimitivo.REAL and t2 == TipoPrimitivo.INTEIRO) or \
       (t1 == TipoPrimitivo.REAL and t2 == TipoPrimitivo.REAL):
        return TipoPrimitivo.REAL
    return TipoPrimitivo.DESCONHECIDO

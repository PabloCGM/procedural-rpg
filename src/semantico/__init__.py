"""Pacote do sistema semântico."""

from src.semantico.tipos import TipoPrimitivo, TipoEntidade, promover_aritmetica, eh_numerico
from src.semantico.simbolos import (
    SimboloCampo,
    SimboloMarco,
    SimboloOperacao,
    SimboloEntidade,
    TabelaSimbolos,
)

__all__ = [
    "TipoPrimitivo",
    "TipoEntidade",
    "promover_aritmetica",
    "eh_numerico",
    "SimboloCampo",
    "SimboloMarco",
    "SimboloOperacao",
    "SimboloEntidade",
    "TabelaSimbolos",
]

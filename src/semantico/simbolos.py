"""Tabela de símbolos e definições de escopo para Procedural RPG (E4)."""

from dataclasses import dataclass, field
from typing import Any
from src.semantico.tipos import TipoPrimitivo, TipoEntidade


@dataclass
class SimboloCampo:
    nome: str
    tipo: TipoPrimitivo
    valor_inicial: Any
    linha: int
    coluna: int


@dataclass
class SimboloMarco:
    id_marco: str
    nome_variavel: str
    descricao: str
    historia_pai: str
    condicao_ctx: Any
    dependencias: list[str] = field(default_factory=list)
    linha: int = 0
    coluna: int = 0


@dataclass
class SimboloOperacao:
    id_operacao: str
    caminho: str
    historia_pai: str
    requer_ctx: Any
    instrucoes_ctx: list[Any] = field(default_factory=list)
    linha: int = 0
    coluna: int = 0


@dataclass
class SimboloEntidade:
    tipo: TipoEntidade
    id_instancia: str
    nome_variavel: str
    pai_variavel: str | None = None
    propriedades: dict[str, Any] = field(default_factory=dict)
    estado: dict[str, SimboloCampo] = field(default_factory=dict)
    ficha: dict[str, SimboloCampo] = field(default_factory=dict)
    participantes: list[str] = field(default_factory=list)
    filhos: dict[str, "SimboloEntidade"] = field(default_factory=dict)
    linha: int = 0
    coluna: int = 0


class TabelaSimbolos:
    def __init__(self):
        # Mapeia nomes de variáveis de escopo superior/global -> SimboloEntidade ou Tipo
        self.variaveis: dict[str, SimboloEntidade] = {}
        # Mapeia id_marco -> SimboloMarco
        self.marcos: dict[str, SimboloMarco] = {}
        # Mapeia caminho de operação -> SimboloOperacao
        self.operacoes: dict[str, SimboloOperacao] = {}
        # Regras de encerramento por história (historia_var -> ctx)
        self.encerramentos: dict[str, tuple[Any, int, int]] = {}

    def definir_variavel(self, nome: str, entidade: SimboloEntidade):
        self.variaveis[nome] = entidade

    def obter_variavel(self, nome: str) -> SimboloEntidade | None:
        return self.variaveis.get(nome)

    def resolver_caminho(self, partes: list[str]) -> tuple[Any, TipoPrimitivo | TipoEntidade | None]:
        """
        Resolve caminhos do tipo:
        - ['abismo'] -> SimboloEntidade
        - ['abismo', 'estado', 'selo_rompido'] -> (SimboloCampo, TipoPrimitivo)
        - ['mira', 'ficha', 'folego'] -> (SimboloCampo, TipoPrimitivo)
        - ['descida', 'jogadores', 'mira'] -> (SimboloEntidade, TipoEntidade)
        - ['saudacao', 'concluido'] -> (None, TipoPrimitivo.BOOLEANO)
        """
        if not partes:
            return None, None

        primeiro = partes[0]
        # Caso especial marco.concluido
        if len(partes) == 2 and partes[1] == "concluido":
            if primeiro in self.marcos or primeiro in self.variaveis:
                return None, TipoPrimitivo.BOOLEANO

        if primeiro not in self.variaveis:
            # Pode ser um marco diretamente acessado pelo nome da variável
            if primeiro in self.marcos:
                return self.marcos[primeiro], TipoEntidade.MARCO
            return None, None

        atual: Any = self.variaveis[primeiro]
        for i in range(1, len(partes)):
            parte = partes[i]
            if isinstance(atual, SimboloEntidade):
                if parte == "estado":
                    atual = atual.estado
                elif parte == "ficha":
                    atual = atual.ficha
                elif parte in ("campanhas", "cenarios", "personagens", "jogadores", "historias", "capitulos", "marcos", "cenas", "itens"):
                    # Coleção de filhos
                    atual = atual.filhos
                elif parte in atual.filhos:
                    atual = atual.filhos[parte]
                elif parte in atual.propriedades:
                    return atual.propriedades[parte], TipoPrimitivo.TEXTO
                else:
                    return None, None
            elif isinstance(atual, dict):
                if parte in atual:
                    atual = atual[parte]
                else:
                    return None, None
            else:
                return None, None

        if isinstance(atual, SimboloCampo):
            return atual, atual.tipo
        if isinstance(atual, SimboloEntidade):
            return atual, atual.tipo
        if isinstance(atual, SimboloMarco):
            return atual, TipoEntidade.MARCO

        return atual, None

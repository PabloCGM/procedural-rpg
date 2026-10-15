"""Extração estrutural e narrativa a partir da Árvore Sintática (prévia para E4)."""

from typing import Any
from antlr4.tree.Tree import TerminalNodeImpl

from gerado.SuaLingParser import SuaLingParser


def _obter_texto_no(no: Any, texto_fonte: str) -> str:
    """Extrai o trecho exato do código-fonte delimitado pelos tokens do nó."""
    if no is None:
        return ""
    start = getattr(no, "start", None)
    stop = getattr(no, "stop", None)
    if start is None or stop is None:
        return ""
    start_idx = getattr(start, "start", None)
    stop_idx = getattr(stop, "stop", None)
    if start_idx is not None and stop_idx is not None and 0 <= start_idx <= stop_idx < len(texto_fonte):
        return texto_fonte[start_idx : stop_idx + 1]
    return getattr(no, "getText", lambda: "")()


def _extrair_chamada_info(expr_no: Any) -> tuple[str, str, str | None]:
    """
    Inspeciona uma expressão de criação do tipo 'Universo("x")' ou 'pai.tipo("x")'.
    Retorna (tipo_entidade, id_entidade, variavel_pai).
    """
    # Caso 1: ExprChamada
    if type(expr_no).__name__ == "ExprChamadaContext":
        filhos = expr_no.children or []
        funcao_alvo = filhos[0]
        arg_id = ""
        # Verifica argumentos
        for f in filhos:
            if type(f).__name__ == "Lista_argumentosContext":
                arg_id = f.getText().strip('"\'')
                break

        # Caso Universo(...)
        if type(funcao_alvo).__name__ == "ExprIdentificadorContext":
            return funcao_alvo.getText(), arg_id, None

        # Caso pai.metodo(...)
        if type(funcao_alvo).__name__ == "ExprAcessoMembroContext":
            partes = funcao_alvo.children or []
            pai_expr = partes[0].getText()
            metodo = partes[2].getText()
            return metodo, arg_id, pai_expr

    return "entidade", "", None


class ExtratorNarrativo:
    def __init__(self, texto_fonte: str):
        self.texto_fonte = texto_fonte
        self.entidades: list[dict[str, Any]] = []
        self.marcos: dict[str, dict[str, Any]] = {}
        self.operacoes: list[dict[str, Any]] = []
        self.encerramentos: list[dict[str, Any]] = []
        self.comando_iniciar: dict[str, str] | None = None

    def extrair(self, arvore: Any) -> dict[str, Any]:
        if arvore is None:
            return {}

        self._visitar_no(arvore)
        return {
            "entidades": self.entidades,
            "marcos": list(self.marcos.values()),
            "operacoes": self.operacoes,
            "encerramentos": self.encerramentos,
            "iniciar": self.comando_iniciar,
        }

    def _visitar_no(self, no: Any, entidade_atual: dict[str, Any] | None = None):
        if no is None or isinstance(no, TerminalNodeImpl):
            return

        classe = type(no).__name__

        if classe == "Declaracao_entidadeContext":
            var_nome = no.IDENT().getText()
            expr_no = no.expr()
            tipo_entidade, id_entidade, pai = _extrair_chamada_info(expr_no)

            nova_entidade = {
                "variavel": var_nome,
                "tipo": tipo_entidade.lower(),
                "id": id_entidade or var_nome,
                "pai": pai,
                "propriedades": {},
                "estados": [],
                "participantes": [],
                "filhos": [],
                "linha": no.start.line if no.start else 1,
            }

            if tipo_entidade.lower() == "marco":
                self.marcos[var_nome] = {
                    "id": id_entidade or var_nome,
                    "variavel": var_nome,
                    "descricao": "",
                    "condicao": None,
                    "dependencias": [],
                    "linha": no.start.line if no.start else 1,
                }

            if entidade_atual is not None:
                entidade_atual["filhos"].append(nova_entidade)
            else:
                self.entidades.append(nova_entidade)

            bloco = no.bloco_entidade()
            if bloco:
                for membro in getattr(bloco, "membro_entidade", lambda: [])():
                    self._visitar_membro(membro, nova_entidade)
            return

        if classe == "Comando_iniciarContext":
            exprs = no.expr()
            if len(exprs) >= 2:
                self.comando_iniciar = {
                    "campanha": exprs[0].getText(),
                    "historia": exprs[1].getText(),
                }
            return

        # Visita recursiva para outros nós
        if hasattr(no, "children") and no.children:
            for filho in no.children:
                self._visitar_no(filho, entidade_atual)

    def _visitar_membro(self, membro_no: Any, entidade: dict[str, Any]):
        classe = type(membro_no).__name__
        filhos = membro_no.children or []
        if not filhos:
            return

        primeiro_filho = filhos[0]
        tipo_filho = type(primeiro_filho).__name__

        # Subentidade
        if tipo_filho == "Declaracao_entidadeContext":
            self._visitar_no(primeiro_filho, entidade)
            return

        # Atribuição simples de propriedade
        if tipo_filho == "AtribuicaoContext":
            texto_attr = primeiro_filho.getText()
            partes = texto_attr.split("=", 1)
            if len(partes) == 2:
                chave = partes[0].strip()
                val = partes[1].strip().strip('"\'')
                entidade["propriedades"][chave] = val
                # Se for propriedade de marco (ex: descricao = "...")
                if entidade["variavel"] in self.marcos and chave == "descricao":
                    self.marcos[entidade["variavel"]]["descricao"] = val
            return

        # Declaração de estado
        if tipo_filho == "Declaracao_estadoContext":
            tipo_d = primeiro_filho.tipo_dado().getText()
            caminho_e = primeiro_filho.caminho().getText()
            val_e = _obter_texto_no(primeiro_filho.expr(), self.texto_fonte)
            entidade["estados"].append({
                "tipo": tipo_d,
                "caminho": caminho_e,
                "valor": val_e,
            })
            return

        # Regra de marco: concluir marco quando expr
        if tipo_filho == "Regra_conclusao_marcoContext":
            alvo = primeiro_filho.IDENT().getText()
            cond = _obter_texto_no(primeiro_filho.expr(), self.texto_fonte)
            if alvo in self.marcos:
                self.marcos[alvo]["condicao"] = cond
            else:
                self.marcos[alvo] = {
                    "id": alvo,
                    "variavel": alvo,
                    "descricao": "",
                    "condicao": cond,
                    "dependencias": [],
                    "linha": primeiro_filho.start.line if primeiro_filho.start else 1,
                }
            return

        # Regra de encerramento: encerrar historia quando expr
        if tipo_filho == "Regra_encerramento_historiaContext":
            alvo = primeiro_filho.IDENT().getText()
            cond = _obter_texto_no(primeiro_filho.expr(), self.texto_fonte)
            self.encerramentos.append({
                "historia": alvo,
                "condicao": cond,
            })
            return

        # Declaração de operação
        if tipo_filho == "Declaracao_operacaoContext":
            caminho_op = primeiro_filho.caminho().getText()
            bloco_op = primeiro_filho.bloco_operacao()
            requer_cond = _obter_texto_no(bloco_op.clausula_requer().expr(), self.texto_fonte)
            instrucoes = []
            for instr in getattr(bloco_op, "instrucao_operacao", lambda: [])():
                instrucoes.append(_obter_texto_no(instr, self.texto_fonte).strip())

            self.operacoes.append({
                "caminho": caminho_op,
                "requer": requer_cond,
                "instrucoes": instrucoes,
                "linha": primeiro_filho.start.line if primeiro_filho.start else 1,
            })
            return

        # Chamada de método (ex: adicionar participantes ou depende_de)
        if hasattr(primeiro_filho, "getText"):
            txt = primeiro_filho.getText()
            if "depende_de(" in txt:
                # Extrai dependência entre marcos: m.depende_de(n)
                partes = txt.split(".depende_de(")
                if len(partes) == 2:
                    m_alvo = partes[0].strip()
                    m_dep = partes[1].rstrip(")").strip()
                    if m_alvo in self.marcos and m_dep not in self.marcos[m_alvo]["dependencias"]:
                        self.marcos[m_alvo]["dependencias"].append(m_dep)
            elif "participantes.adicionar(" in txt:
                partes = txt.split("participantes.adicionar(")
                if len(partes) == 2:
                    p = partes[1].rstrip(")").strip()
                    entidade["participantes"].append(p)


def extrair_estrutura_narrativa(arvore: Any, texto_fonte: str) -> dict[str, Any]:
    """Função pública que extrai a estrutura narrativa completa da árvore sintática."""
    extrator = ExtratorNarrativo(texto_fonte)
    return extrator.extrair(arvore)

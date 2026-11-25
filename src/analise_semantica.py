"""Análise semântica completa para o compilador Procedural RPG (E4)."""

from dataclasses import dataclass, field
from typing import Any

from antlr4.tree.Tree import TerminalNodeImpl
from gerado.SuaLingParser import SuaLingParser
from gerado.SuaLingParserVisitor import SuaLingParserVisitor
from src.analise_lexica import Diagnostico
from src.semantico.simbolos import (
    SimboloCampo,
    SimboloEntidade,
    SimboloMarco,
    SimboloOperacao,
    TabelaSimbolos,
)
from src.semantico.tipos import TipoEntidade, TipoPrimitivo, eh_numerico, promover_aritmetica


METODOS_PERMITIDOS: dict[TipoEntidade, dict[str, TipoEntidade]] = {
    TipoEntidade.UNIVERSO: {
        "campanha": TipoEntidade.CAMPANHA,
        "cenario": TipoEntidade.CENARIO,
        "personagem": TipoEntidade.PERSONAGEM,
    },
    TipoEntidade.CAMPANHA: {
        "jogador": TipoEntidade.PERSONAGEM,
        "historia": TipoEntidade.HISTORIA,
    },
    TipoEntidade.HISTORIA: {
        "capitulo": TipoEntidade.CAPITULO,
        "marco": TipoEntidade.MARCO,
        "personagem": TipoEntidade.PERSONAGEM,
    },
    TipoEntidade.CAPITULO: {
        "cena": TipoEntidade.CENA,
        "personagem": TipoEntidade.PERSONAGEM,
    },
    TipoEntidade.CENA: {
        "personagem": TipoEntidade.PERSONAGEM,
    },
    TipoEntidade.INVENTARIO: {
        "item": TipoEntidade.ITEM,
    },
}


@dataclass
class ResultadoSemantico:
    sucesso: bool
    erros: list[Diagnostico]
    tabela: TabelaSimbolos
    campanha_iniciar: str | None = None
    historia_iniciar: str | None = None


def _posicao(ctx: Any) -> tuple[int, int]:
    if ctx is None:
        return 1, 1
    start = getattr(ctx, "start", None)
    if start is not None:
        linha = getattr(start, "line", 1)
        coluna = getattr(start, "column", 0) + 1
        return linha, coluna
    return 1, 1


class ColetorDeclaracoesVisitor(SuaLingParserVisitor):
    """Passo 1: Coleta entidades, variáveis, estados, marcos e operações na Tabela de Símbolos."""

    def __init__(self, tabela: TabelaSimbolos, erros: list[Diagnostico]):
        self.tabela = tabela
        self.erros = erros
        self.pilha_entidades: list[SimboloEntidade] = []

    def _processar_declaracao_ou_atribuicao_entidade(self, nome_var: str, expr_chamada: Any, ctx_pos: Any, bloco_ctx: Any = None):
        linha, coluna = _posicao(ctx_pos)
        tipo_entidade = TipoEntidade.DESCONHECIDO
        id_instancia = ""
        pai_var = None
        pai_entidade = None

        if isinstance(expr_chamada, SuaLingParser.ExprChamadaContext):
            alvo = expr_chamada.expr()
            args = expr_chamada.lista_argumentos()
            if args:
                id_instancia = args.getText().strip('"\'')

            if isinstance(alvo, SuaLingParser.ExprIdentificadorContext):
                nome_alvo = alvo.IDENT().getText()
                if nome_alvo == "Universo":
                    tipo_entidade = TipoEntidade.UNIVERSO
                else:
                    self.erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"construtor desconhecido '{nome_alvo}'. Apenas 'Universo' pode ser instanciado diretamente.",
                        )
                    )
            elif isinstance(alvo, SuaLingParser.ExprAcessoMembroContext):
                metodo = alvo.IDENT().getText()
                pai_expr_ctx = alvo.expr()
                partes_receptor = []
                curr = pai_expr_ctx
                while isinstance(curr, SuaLingParser.ExprAcessoMembroContext):
                    partes_receptor.append(curr.IDENT().getText())
                    curr = curr.expr()
                if isinstance(curr, SuaLingParser.ExprIdentificadorContext):
                    partes_receptor.append(curr.IDENT().getText())
                partes_receptor.reverse()
                pai_var = ".".join(partes_receptor)

                # Caso especial <personagem>.inventario.item(...)
                if len(partes_receptor) == 2 and partes_receptor[1] == "inventario":
                    dono_var = partes_receptor[0]
                    dono_entidade = self.tabela.obter_variavel(dono_var)
                    if dono_entidade and dono_entidade.tipo == TipoEntidade.PERSONAGEM and metodo == "item":
                        tipo_entidade = TipoEntidade.ITEM
                        pai_entidade = dono_entidade
                    else:
                        pai_entidade = None
                else:
                    pai_entidade = self.tabela.obter_variavel(pai_var)

                if not pai_entidade:
                    self.erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"objeto receptor '{pai_var}' não declarado antes de criar '{nome_var}'.",
                        )
                    )
                elif tipo_entidade == TipoEntidade.DESCONHECIDO:
                    metodos_validos = METODOS_PERMITIDOS.get(pai_entidade.tipo, {})
                    if metodo not in metodos_validos:
                        self.erros.append(
                            Diagnostico(
                                "semântico",
                                linha,
                                coluna,
                                f"receptor '{pai_entidade.tipo.value}' não possui método de criação '{metodo}'.",
                            )
                        )
                    else:
                        tipo_entidade = metodos_validos[metodo]

        entidade = SimboloEntidade(
            tipo=tipo_entidade,
            id_instancia=id_instancia,
            nome_variavel=nome_var,
            pai_variavel=pai_var,
            linha=linha,
            coluna=coluna,
        )

        self.tabela.definir_variavel(nome_var, entidade)
        if pai_entidade:
            pai_entidade.filhos[id_instancia] = entidade
        elif self.pilha_entidades:
            pai_topo = self.pilha_entidades[-1]
            pai_topo.filhos[id_instancia] = entidade

        if tipo_entidade == TipoEntidade.MARCO:
            historia_pai = self.pilha_entidades[-1].nome_variavel if self.pilha_entidades else ""
            self.tabela.marcos[nome_var] = SimboloMarco(
                id_marco=id_instancia,
                nome_variavel=nome_var,
                descricao="",
                historia_pai=historia_pai,
                condicao_ctx=None,
                linha=linha,
                coluna=coluna,
            )

        if bloco_ctx:
            self.pilha_entidades.append(entidade)
            self.visitBloco_entidade(bloco_ctx)
            self.pilha_entidades.pop()

    def visitDeclaracao_estado(self, ctx: SuaLingParser.Declaracao_estadoContext):
        tipo_str = ctx.tipo_dado().getText()
        tipo_prim = TipoPrimitivo(tipo_str)
        partes = [id_tok.getText() for id_tok in ctx.caminho().IDENT()]
        linha, coluna = _posicao(ctx.caminho())

        if len(partes) != 3 or partes[1] not in ("estado", "ficha"):
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"caminho de declaração de estado inválido '{'.'.join(partes)}'. Formato esperado: '<objeto>.estado.<campo>' ou '<objeto>.ficha.<campo>'",
                )
            )
            return

        obj_nome, categoria, campo_nome = partes
        entidade = self.tabela.obter_variavel(obj_nome)
        if not entidade:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"objeto '{obj_nome}' não declarado para definir {categoria}.")
            )
            return

        alvo_dict = entidade.estado if categoria == "estado" else entidade.ficha
        if campo_nome in alvo_dict:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"campo '{campo_nome}' já declarado em '{obj_nome}.{categoria}'.")
            )
            return

        alvo_dict[campo_nome] = SimboloCampo(
            nome=campo_nome,
            tipo=tipo_prim,
            valor_inicial=None,
            linha=linha,
            coluna=coluna,
        )

    def visitRegra_conclusao_marco(self, ctx: SuaLingParser.Regra_conclusao_marcoContext):
        nome_marco = ctx.IDENT().getText()
        linha, coluna = _posicao(ctx.IDENT())

        if nome_marco not in self.tabela.marcos and nome_marco not in self.tabela.variaveis:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"marco '{nome_marco}' não foi declarado.")
            )
            return

        if nome_marco in self.tabela.marcos:
            marco = self.tabela.marcos[nome_marco]
            if marco.condicao_ctx is not None:
                self.erros.append(
                    Diagnostico("semântico", linha, coluna, f"marco '{nome_marco}' já possui condição de conclusão definida.")
                )
            marco.condicao_ctx = ctx.expr()

    def visitRegra_encerramento_historia(self, ctx: SuaLingParser.Regra_encerramento_historiaContext):
        nome_historia = ctx.IDENT().getText()
        linha, coluna = _posicao(ctx.IDENT())

        entidade = self.tabela.obter_variavel(nome_historia)
        if not entidade or entidade.tipo != TipoEntidade.HISTORIA:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"identificador '{nome_historia}' não é uma história válida para encerrar.")
            )
            return

        if nome_historia in self.tabela.encerramentos:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"história '{nome_historia}' já possui regra de encerramento.")
            )
        self.tabela.encerramentos[nome_historia] = (ctx.expr(), linha, coluna)

    def visitDeclaracao_operacao(self, ctx: SuaLingParser.Declaracao_operacaoContext):
        partes = [id_tok.getText() for id_tok in ctx.caminho().IDENT()]
        linha, coluna = _posicao(ctx.caminho())

        if len(partes) != 2:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"caminho de operação inválido '{'.'.join(partes)}'. Esperado: '<historia>.<nome_operacao>'",
                )
            )
            return

        historia_nome, op_nome = partes
        caminho_str = f"{historia_nome}.{op_nome}"
        if caminho_str in self.tabela.operacoes:
            self.erros.append(
                Diagnostico("semântico", linha, coluna, f"operação '{caminho_str}' já foi declarada.")
            )
            return

        bloco = ctx.bloco_operacao()
        requer_ctx = bloco.clausula_requer().expr()
        instrucoes = bloco.instrucao_operacao() or []

        self.tabela.operacoes[caminho_str] = SimboloOperacao(
            id_operacao=op_nome,
            caminho=caminho_str,
            historia_pai=historia_nome,
            requer_ctx=requer_ctx,
            instrucoes_ctx=instrucoes,
            linha=linha,
            coluna=coluna,
        )

    def visitDeclaracao_entidade(self, ctx: SuaLingParser.Declaracao_entidadeContext):
        nome_var = ctx.IDENT().getText()
        self._processar_declaracao_ou_atribuicao_entidade(
            nome_var, ctx.expr(), ctx.IDENT(), ctx.bloco_entidade()
        )

    def visitAtribuicao(self, ctx: SuaLingParser.AtribuicaoContext):
        partes = [id_tok.getText() for id_tok in ctx.caminho().IDENT()]
        if len(partes) == 1 and isinstance(ctx.expr(), SuaLingParser.ExprChamadaContext):
            # É uma criação de entidade sem bloco filho (ex: ola = jornada.historia("ola"))
            self._processar_declaracao_ou_atribuicao_entidade(partes[0], ctx.expr(), ctx.caminho())
            return

        if len(partes) == 1 and self.pilha_entidades:
            entidade_atual = self.pilha_entidades[-1]
            entidade_atual.propriedades[partes[0]] = ctx.expr().getText()

        # Atribuição avulsa de alias (ex: jornada = vila.campanhas.jornada)
        if len(partes) == 1 and not self.pilha_entidades:
            nome_var = partes[0]
            expr_alvo = ctx.expr()
            txt = expr_alvo.getText()
            partes_expr = txt.split(".")
            simb, _ = self.tabela.resolver_caminho(partes_expr)
            if isinstance(simb, SimboloEntidade):
                self.tabela.definir_variavel(nome_var, simb)


class VerificadorTiposVisitor(SuaLingParserVisitor):
    """Passo 2: Verificação de tipos estáticos em expressões, instruções e validações de regras."""

    def __init__(self, tabela: TabelaSimbolos, erros: list[Diagnostico]):
        self.tabela = tabela
        self.erros = erros

    def obter_tipo_expr(self, ctx: Any) -> TipoPrimitivo | TipoEntidade:
        if ctx is None:
            return TipoPrimitivo.DESCONHECIDO

        linha, coluna = _posicao(ctx)

        # Parenteses
        if isinstance(ctx, SuaLingParser.ExprParentesesContext):
            return self.obter_tipo_expr(ctx.expr())

        # Literal
        if isinstance(ctx, SuaLingParser.ExprLiteralContext):
            lit = ctx.literal()
            if lit.INTEIRO():
                return TipoPrimitivo.INTEIRO
            if lit.REAL():
                return TipoPrimitivo.REAL
            if lit.TEXTO():
                return TipoPrimitivo.TEXTO
            if lit.VERDADEIRO() or lit.FALSO():
                return TipoPrimitivo.BOOLEANO

        # Identificador simples
        if isinstance(ctx, SuaLingParser.ExprIdentificadorContext):
            nome = ctx.IDENT().getText()
            simb, tipo = self.tabela.resolver_caminho([nome])
            if simb is None and tipo is None:
                self.erros.append(
                    Diagnostico("semântico", linha, coluna, f"identificador '{nome}' não declarado neste escopo.")
                )
                return TipoPrimitivo.DESCONHECIDO
            return tipo or TipoPrimitivo.DESCONHECIDO

        # Acesso a Membro (caminho com ponto)
        if isinstance(ctx, SuaLingParser.ExprAcessoMembroContext):
            partes = self._coletar_partes_membro(ctx)
            simb, tipo = self.tabela.resolver_caminho(partes)
            if simb is None and tipo is None:
                caminho_fmt = ".".join(partes)
                self.erros.append(
                    Diagnostico("semântico", linha, coluna, f"caminho ou membro '{caminho_fmt}' inexistente ou inacessível.")
                )
                return TipoPrimitivo.DESCONHECIDO
            return tipo or TipoPrimitivo.DESCONHECIDO

        # Unária (+ ou -)
        if isinstance(ctx, SuaLingParser.ExprUnariaContext):
            tipo_sub = self.obter_tipo_expr(ctx.expr())
            if not eh_numerico(tipo_sub):
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"operador unário aplicado a tipo não numérico '{tipo_sub.value}'.",
                    )
                )
                return TipoPrimitivo.DESCONHECIDO
            return tipo_sub

        # Multiplicativa (* ou /)
        if isinstance(ctx, SuaLingParser.ExprMultiplicativaContext):
            t1 = self.obter_tipo_expr(ctx.expr(0))
            t2 = self.obter_tipo_expr(ctx.expr(1))
            op = ctx.MULTIPLICACAO() or ctx.DIVISAO()
            op_str = op.getText() if op else "*"

            if not (eh_numerico(t1) and eh_numerico(t2)):
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"tipos incompatíveis para operador '{op_str}': '{t1.value}' e '{t2.value}'. Ambos devem ser numéricos.",
                    )
                )
                return TipoPrimitivo.DESCONHECIDO

            if op_str == "/":
                return TipoPrimitivo.REAL
            return promover_aritmetica(t1, t2)

        # Aditiva (+ ou -)
        if isinstance(ctx, SuaLingParser.ExprAditivaContext):
            t1 = self.obter_tipo_expr(ctx.expr(0))
            t2 = self.obter_tipo_expr(ctx.expr(1))
            op = ctx.MAIS() or ctx.MENOS()
            op_str = op.getText() if op else "+"

            # Caso especial: soma de textos (concatenação)
            if op_str == "+":
                if t1 == TipoPrimitivo.TEXTO and t2 == TipoPrimitivo.TEXTO:
                    return TipoPrimitivo.TEXTO
                if t1 == TipoPrimitivo.TEXTO or t2 == TipoPrimitivo.TEXTO:
                    self.erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"tipos incompatíveis para operador '+': '{t1.value}' e '{t2.value}'. Não é permitida coerção implícita entre texto e número.",
                        )
                    )
                    return TipoPrimitivo.DESCONHECIDO

            if not (eh_numerico(t1) and eh_numerico(t2)):
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"tipos incompatíveis para operador '{op_str}': '{t1.value}' e '{t2.value}'. Ambos devem ser numéricos.",
                    )
                )
                return TipoPrimitivo.DESCONHECIDO

            return promover_aritmetica(t1, t2)

        # Relacional (<, <=, >, >=, ==, !=)
        if isinstance(ctx, SuaLingParser.ExprRelacionalContext):
            t1 = self.obter_tipo_expr(ctx.expr(0))
            t2 = self.obter_tipo_expr(ctx.expr(1))
            op_rel = ctx.op_relacional().getText()

            if op_rel in ("<", "<=", ">", ">="):
                if not (eh_numerico(t1) and eh_numerico(t2)):
                    self.erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"comparação de ordem '{op_rel}' exige operandos numéricos, recebido '{t1.value}' e '{t2.value}'.",
                        )
                    )
                    return TipoPrimitivo.BOOLEANO
            elif op_rel in ("==", "!="):
                # Permite entre numéricos compatíveis, ou tipos idênticos
                ambos_num = eh_numerico(t1) and eh_numerico(t2)
                mesmo_tipo = (t1 == t2)
                if not (ambos_num or mesmo_tipo):
                    self.erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"comparação de igualdade '{op_rel}' entre tipos incompatíveis: '{t1.value}' e '{t2.value}'.",
                        )
                    )
            return TipoPrimitivo.BOOLEANO

        # Negação (nao)
        if isinstance(ctx, SuaLingParser.ExprNaoContext):
            tipo_sub = self.obter_tipo_expr(ctx.expr())
            if tipo_sub != TipoPrimitivo.BOOLEANO:
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"operador 'nao' exige operando do tipo 'booleano', recebido '{tipo_sub.value}'.",
                    )
                )
            return TipoPrimitivo.BOOLEANO

        # Lógicos (e, ou)
        if isinstance(ctx, (SuaLingParser.ExprEContext, SuaLingParser.ExprOuContext)):
            t1 = self.obter_tipo_expr(ctx.expr(0))
            t2 = self.obter_tipo_expr(ctx.expr(1))
            op_nome = "e" if isinstance(ctx, SuaLingParser.ExprEContext) else "ou"
            if t1 != TipoPrimitivo.BOOLEANO or t2 != TipoPrimitivo.BOOLEANO:
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"operador lógico '{op_nome}' exige operandos booleanos, recebido '{t1.value}' e '{t2.value}'.",
                    )
                )
            return TipoPrimitivo.BOOLEANO

        return TipoPrimitivo.DESCONHECIDO

    def _coletar_partes_membro(self, ctx: SuaLingParser.ExprAcessoMembroContext) -> list[str]:
        partes = []
        atual = ctx
        while isinstance(atual, SuaLingParser.ExprAcessoMembroContext):
            partes.append(atual.IDENT().getText())
            atual = atual.expr()
        if isinstance(atual, SuaLingParser.ExprIdentificadorContext):
            partes.append(atual.IDENT().getText())
        elif hasattr(atual, "getText"):
            partes.append(atual.getText())
        partes.reverse()
        return partes

    def visitDeclaracao_estado(self, ctx: SuaLingParser.Declaracao_estadoContext):
        tipo_declarado = TipoPrimitivo(ctx.tipo_dado().getText())
        tipo_expr = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())

        if tipo_expr != TipoPrimitivo.DESCONHECIDO and not self._tipos_compativeis(tipo_declarado, tipo_expr):
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"atribuição de tipo incompatível na inicialização: esperado '{tipo_declarado.value}', recebido '{tipo_expr.value}'.",
                )
            )

    def visitAtribuicao(self, ctx: SuaLingParser.AtribuicaoContext):
        partes = [id_tok.getText() for id_tok in ctx.caminho().IDENT()]
        linha, coluna = _posicao(ctx.caminho())

        if len(partes) >= 2 and partes[1] in ("estado", "ficha"):
            simb, tipo_campo = self.tabela.resolver_caminho(partes)
            if not simb:
                self.erros.append(
                    Diagnostico("semântico", linha, coluna, f"campo '{'.'.join(partes)}' não foi declarado.")
                )
                return

            tipo_expr = self.obter_tipo_expr(ctx.expr())
            if tipo_expr != TipoPrimitivo.DESCONHECIDO and not self._tipos_compativeis(tipo_campo, tipo_expr):
                self.erros.append(
                    Diagnostico(
                        "semântico",
                        linha,
                        coluna,
                        f"atribuição de tipo incompatível para '{'.'.join(partes)}': esperado '{tipo_campo.value}', recebido '{tipo_expr.value}'.",
                    )
                )

    def visitComando_narrar(self, ctx: SuaLingParser.Comando_narrarContext):
        tipo_expr = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())
        if tipo_expr != TipoPrimitivo.DESCONHECIDO and tipo_expr != TipoPrimitivo.TEXTO:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"comando 'narrar' exige expressão do tipo 'texto', recebido '{tipo_expr.value}'.",
                )
            )

    def visitComando_se(self, ctx: SuaLingParser.Comando_seContext):
        tipo_cond = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())
        if tipo_cond != TipoPrimitivo.DESCONHECIDO and tipo_cond != TipoPrimitivo.BOOLEANO:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"condição do comando 'se' deve ser do tipo 'booleano', recebido '{tipo_cond.value}'.",
                )
            )
        self.visitChildren(ctx)

    def visitClausula_requer(self, ctx: SuaLingParser.Clausula_requerContext):
        tipo_req = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())
        if tipo_req != TipoPrimitivo.DESCONHECIDO and tipo_req != TipoPrimitivo.BOOLEANO:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"cláusula 'requer' exige expressão do tipo 'booleano', recebido '{tipo_req.value}'.",
                )
            )

    def visitRegra_conclusao_marco(self, ctx: SuaLingParser.Regra_conclusao_marcoContext):
        tipo_cond = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())
        if tipo_cond != TipoPrimitivo.DESCONHECIDO and tipo_cond != TipoPrimitivo.BOOLEANO:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"condição de conclusão de marco deve ser do tipo 'booleano', recebido '{tipo_cond.value}'.",
                )
            )

    def visitRegra_encerramento_historia(self, ctx: SuaLingParser.Regra_encerramento_historiaContext):
        tipo_cond = self.obter_tipo_expr(ctx.expr())
        linha, coluna = _posicao(ctx.expr())
        if tipo_cond != TipoPrimitivo.DESCONHECIDO and tipo_cond != TipoPrimitivo.BOOLEANO:
            self.erros.append(
                Diagnostico(
                    "semântico",
                    linha,
                    coluna,
                    f"condição de encerramento da história deve ser do tipo 'booleano', recebido '{tipo_cond.value}'.",
                )
            )

    def _tipos_compativeis(self, esperado: Any, recebido: Any) -> bool:
        if esperado == recebido:
            return True
        if esperado == TipoPrimitivo.REAL and recebido == TipoPrimitivo.INTEIRO:
            return True
        return False


def validar_dependencias_marcos(arvore: Any, tabela: TabelaSimbolos, erros: list[Diagnostico]):
    """Extrai chamadas `marco.depende_de(outro)` e valida ausência de ciclos."""
    # Posição de cada chamada `origem.depende_de(dep)`, usada para localizar os erros.
    posicoes: dict[tuple[str, str], tuple[int, int]] = {}

    class ExtratorDependenciasVisitor(SuaLingParserVisitor):
        def visitExprChamada(self, ctx: SuaLingParser.ExprChamadaContext):
            alvo = ctx.expr()
            if isinstance(alvo, SuaLingParser.ExprAcessoMembroContext):
                metodo = alvo.IDENT().getText()
                if metodo == "depende_de":
                    marco_origem = alvo.expr().getText()
                    args = ctx.lista_argumentos()
                    if args:
                        marco_dep = args.getText().strip()
                        linha, coluna = _posicao(ctx)
                        posicoes.setdefault((marco_origem, marco_dep), (linha, coluna))

                        if marco_origem in tabela.marcos:
                            tabela.marcos[marco_origem].dependencias.append(marco_dep)
                            if marco_origem == marco_dep:
                                erros.append(
                                    Diagnostico(
                                        "semântico",
                                        linha,
                                        coluna,
                                        f"auto-dependência inválida: marco '{marco_origem}' não pode depender de si mesmo.",
                                    )
                                )
                        else:
                            erros.append(
                                Diagnostico(
                                    "semântico",
                                    linha,
                                    coluna,
                                    f"marco de origem '{marco_origem}' desconhecido para dependência.",
                                )
                            )
            return self.visitChildren(ctx)

    extrator = ExtratorDependenciasVisitor()
    extrator.visit(arvore)

    # Detecção de ciclos via DFS
    grafo: dict[str, list[str]] = {m: list(info.dependencias) for m, info in tabela.marcos.items()}
    visitado: set[str] = set()
    pilha_rec: set[str] = set()

    def dfs(nodo: str, caminho: list[str]) -> bool:
        visitado.add(nodo)
        pilha_rec.add(nodo)
        caminho.append(nodo)

        for vizinho in grafo.get(nodo, []):
            if vizinho not in tabela.marcos:
                l, c = posicoes.get((nodo, vizinho), (1, 1))
                erros.append(
                    Diagnostico(
                        "semântico",
                        l,
                        c,
                        f"marco pré-requisito '{vizinho}' não encontrado na história.",
                    )
                )
                continue

            if vizinho in pilha_rec:
                l, c = posicoes.get((nodo, vizinho), (1, 1))
                ciclo_str = " -> ".join(caminho + [vizinho])
                erros.append(
                    Diagnostico(
                        "semântico",
                        l,
                        c,
                        f"dependência cíclica detectada entre marcos: {ciclo_str}.",
                    )
                )
                return True
            if vizinho not in visitado:
                if dfs(vizinho, caminho):
                    return True

        pilha_rec.remove(nodo)
        caminho.pop()
        return False

    for m in grafo:
        if m not in visitado:
            dfs(m, [])


def validar_comando_iniciar(arvore: Any, tabela: TabelaSimbolos, erros: list[Diagnostico]) -> tuple[str | None, str | None]:
    campanha_alvo = None
    historia_alvo = None

    class IniciarVisitor(SuaLingParserVisitor):
        def visitComando_iniciar(self, ctx: SuaLingParser.Comando_iniciarContext):
            nonlocal campanha_alvo, historia_alvo
            linha, coluna = _posicao(ctx)
            exprs = ctx.expr()
            if len(exprs) == 2:
                camp_nome = exprs[0].getText()
                hist_nome = exprs[1].getText()

                simb_camp, _ = tabela.resolver_caminho(camp_nome.split("."))
                simb_hist, _ = tabela.resolver_caminho(hist_nome.split("."))

                if not simb_camp or not isinstance(simb_camp, SimboloEntidade):
                    erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"campanha '{camp_nome}' não declarada para comando 'iniciar'.",
                        )
                    )
                elif simb_camp.tipo != TipoEntidade.CAMPANHA:
                    erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"objeto '{camp_nome}' não é uma Campanha.",
                        )
                    )

                if not simb_hist or not isinstance(simb_hist, SimboloEntidade):
                    erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"história '{hist_nome}' não declarada para comando 'iniciar'.",
                        )
                    )
                elif simb_hist.tipo != TipoEntidade.HISTORIA:
                    erros.append(
                        Diagnostico(
                            "semântico",
                            linha,
                            coluna,
                            f"objeto '{hist_nome}' não é uma História.",
                        )
                    )
                elif simb_camp and isinstance(simb_camp, SimboloEntidade):
                    # Valida se a história realmente pertence à campanha
                    if simb_hist.id_instancia not in simb_camp.filhos:
                        erros.append(
                            Diagnostico(
                                "semântico",
                                linha,
                                coluna,
                                f"história '{hist_nome}' não pertence à campanha '{camp_nome}'.",
                            )
                        )

                campanha_alvo = camp_nome
                historia_alvo = hist_nome

    visitor = IniciarVisitor()
    visitor.visit(arvore)
    return campanha_alvo, historia_alvo


def analisar_semantica(arvore: Any) -> ResultadoSemantico:
    """Executa a análise semântica completa: declarações, tipos, grafo e comando iniciar."""
    tabela = TabelaSimbolos()
    erros: list[Diagnostico] = []

    if arvore is None:
        return ResultadoSemantico(sucesso=False, erros=erros, tabela=tabela)

    # Passo 1: Coleta de declarações
    coletor = ColetorDeclaracoesVisitor(tabela, erros)
    coletor.visit(arvore)

    # Passo 2: Verificação de Tipos
    verificador = VerificadorTiposVisitor(tabela, erros)
    verificador.visit(arvore)

    # Passo 3: Validação do Grafo de Marcos (detecção de ciclos)
    validar_dependencias_marcos(arvore, tabela, erros)

    # Passo 4: Validação do comando iniciar
    camp_iniciar, hist_iniciar = validar_comando_iniciar(arvore, tabela, erros)

    erros.sort(key=lambda erro: (erro.linha, erro.coluna))
    return ResultadoSemantico(
        sucesso=len(erros) == 0,
        erros=erros,
        tabela=tabela,
        campanha_iniciar=camp_iniciar,
        historia_iniciar=hist_iniciar,
    )

"""Motor de Execução (Runtime) e Interpretador de Sessão RPG (E4)."""

from dataclasses import dataclass, field
from typing import Any

from gerado.SuaLingParser import SuaLingParser
from gerado.SuaLingParserVisitor import SuaLingParserVisitor
from src.analise_semantica import ResultadoSemantico
from src.semantico.simbolos import SimboloEntidade


@dataclass
class RespostaOperacao:
    sucesso: bool
    motivo: str
    mensagens_narradas: list[str] = field(default_factory=list)
    marcos_concluidos_nesta_rodada: list[str] = field(default_factory=list)
    historia_encerrada: bool = False


class AvaliadorDinamico(SuaLingParserVisitor):
    """Avalia o valor em tempo de execução de uma expressão ANTLR dado o estado atual."""

    def __init__(self, estado_global: dict[str, Any]):
        self.estado = estado_global

    def visitExprParenteses(self, ctx: SuaLingParser.ExprParentesesContext):
        return self.visit(ctx.expr())

    def visitExprLiteral(self, ctx: SuaLingParser.ExprLiteralContext):
        lit = ctx.literal()
        if lit.INTEIRO():
            return int(lit.INTEIRO().getText())
        if lit.REAL():
            return float(lit.REAL().getText())
        if lit.TEXTO():
            return lit.TEXTO().getText().strip('"')
        if lit.VERDADEIRO():
            return True
        if lit.FALSO():
            return False
        return None

    def visitExprIdentificador(self, ctx: SuaLingParser.ExprIdentificadorContext):
        nome = ctx.IDENT().getText()
        return self.estado.get(nome, None)

    def visitExprAcessoMembro(self, ctx: SuaLingParser.ExprAcessoMembroContext):
        partes = []
        atual = ctx
        while isinstance(atual, SuaLingParser.ExprAcessoMembroContext):
            partes.append(atual.IDENT().getText())
            atual = atual.expr()
        if isinstance(atual, SuaLingParser.ExprIdentificadorContext):
            partes.append(atual.IDENT().getText())
        partes.reverse()

        caminho_fmt = ".".join(partes)
        return self.estado.get(caminho_fmt, None)

    def visitExprUnaria(self, ctx: SuaLingParser.ExprUnariaContext):
        val = self.visit(ctx.expr())
        if ctx.MENOS():
            return -val
        return +val

    def visitExprMultiplicativa(self, ctx: SuaLingParser.ExprMultiplicativaContext):
        v1 = self.visit(ctx.expr(0))
        v2 = self.visit(ctx.expr(1))
        if ctx.DIVISAO():
            if v2 == 0:
                raise ZeroDivisionError("Divisão por zero em tempo de execução.")
            return float(v1) / float(v2)
        return v1 * v2

    def visitExprAditiva(self, ctx: SuaLingParser.ExprAditivaContext):
        v1 = self.visit(ctx.expr(0))
        v2 = self.visit(ctx.expr(1))
        if ctx.MENOS():
            return v1 - v2
        return v1 + v2

    def visitExprRelacional(self, ctx: SuaLingParser.ExprRelacionalContext):
        v1 = self.visit(ctx.expr(0))
        v2 = self.visit(ctx.expr(1))
        op = ctx.op_relacional().getText()
        if op == "<":
            return v1 < v2
        if op == "<=":
            return v1 <= v2
        if op == ">":
            return v1 > v2
        if op == ">=":
            return v1 >= v2
        if op == "==":
            return v1 == v2
        if op == "!=":
            return v1 != v2
        return False

    def visitExprNao(self, ctx: SuaLingParser.ExprNaoContext):
        return not bool(self.visit(ctx.expr()))

    def visitExprE(self, ctx: SuaLingParser.ExprEContext):
        v1 = self.visit(ctx.expr(0))
        if not v1:
            return False
        return bool(self.visit(ctx.expr(1)))

    def visitExprOu(self, ctx: SuaLingParser.ExprOuContext):
        v1 = self.visit(ctx.expr(0))
        if v1:
            return True
        return bool(self.visit(ctx.expr(1)))


class MotorExecucaoRPG:
    """Controla o estado da sessão de RPG, execução de operações e progresso dos marcos."""

    def __init__(self, semantico: ResultadoSemantico, arvore: Any):
        self.semantico = semantico
        self.arvore = arvore
        self.tabela = semantico.tabela
        # Estado dinâmico chave-valor: ex "espiral.estado.raio": 16.0
        self.memoria: dict[str, Any] = {}
        self.status_marcos: dict[str, bool] = {m: False for m in self.tabela.marcos}
        self.historia_encerrada: bool = False
        self.historico_narracao: list[str] = []

        self._inicializar_estado_memoria()
        self.reavaliar_marcos_e_progresso()

    def _inicializar_estado_memoria(self):
        """Inicializa campos de estado e ficha a partir das declarações da árvore."""
        avaliador_estatico = AvaliadorDinamico(self.memoria)

        class ColetorInicialVisitor(SuaLingParserVisitor):
            def __init__(self, memoria: dict[str, Any]):
                self.memoria = memoria

            def visitDeclaracao_estado(self, ctx: SuaLingParser.Declaracao_estadoContext):
                partes = [id_tok.getText() for id_tok in ctx.caminho().IDENT()]
                caminho_fmt = ".".join(partes)
                val = avaliador_estatico.visit(ctx.expr())
                self.memoria[caminho_fmt] = val

        coletor = ColetorInicialVisitor(self.memoria)
        coletor.visit(self.arvore)

    def avaliar_expressao(self, expr_ctx: Any) -> Any:
        avaliador = AvaliadorDinamico(self.memoria)
        return avaliador.visit(expr_ctx)

    def reavaliar_marcos_e_progresso(self) -> list[str]:
        """Reavalia em cascata condições de marcos e encerramento da história."""
        concluidos_novos: list[str] = []
        houve_mudanca = True

        while houve_mudanca:
            houve_mudanca = False
            for nome_marco, marco in self.tabela.marcos.items():
                if self.status_marcos[nome_marco]:
                    continue

                # Verifica se todas as dependências estão concluídas
                deps_ok = all(self.status_marcos.get(dep, False) for dep in marco.dependencias)
                if not deps_ok:
                    continue

                # Avalia condição do marco
                cond_val = True
                if marco.condicao_ctx:
                    cond_val = bool(self.avaliar_expressao(marco.condicao_ctx))

                if cond_val:
                    self.status_marcos[nome_marco] = True
                    # Registra também como <nome_marco>.concluido no escopo
                    self.memoria[f"{nome_marco}.concluido"] = True
                    concluidos_novos.append(nome_marco)
                    houve_mudanca = True

        # Verifica regra de encerramento da história ativa
        historia_alvo = self.semantico.historia_iniciar
        if historia_alvo:
            # extrai apenas o id se for caminho (ex: jornada.historias.ola -> ola)
            hist_id = historia_alvo.split(".")[-1]
            if hist_id in self.tabela.encerramentos:
                ctx_enc, _, _ = self.tabela.encerramentos[hist_id]
                if self.avaliar_expressao(ctx_enc):
                    self.historia_encerrada = True

        return concluidos_novos

    def obter_operacoes_disponiveis(self) -> list[str]:
        """Retorna as operações cujo requer é satisfeito no momento."""
        if self.historia_encerrada:
            return []

        disponiveis = []
        for caminho, op in self.tabela.operacoes.items():
            try:
                requer_ok = bool(self.avaliar_expressao(op.requer_ctx))
                if requer_ok:
                    disponiveis.append(caminho)
            except Exception:
                pass
        return disponiveis

    def executar_operacao(self, caminho_operacao: str) -> RespostaOperacao:
        if self.historia_encerrada:
            return RespostaOperacao(
                sucesso=False,
                motivo=f"A história já foi encerrada. Nenhuma operação permitida.",
                historia_encerrada=True,
            )

        if caminho_operacao not in self.tabela.operacoes:
            return RespostaOperacao(
                sucesso=False,
                motivo=f"Operação '{caminho_operacao}' não encontrada.",
            )

        op = self.tabela.operacoes[caminho_operacao]

        # 1. Checa requer
        if not bool(self.avaliar_expressao(op.requer_ctx)):
            return RespostaOperacao(
                sucesso=False,
                motivo=f"Requisito da operação ('requer') não satisfeito no estado atual.",
            )

        # Snapshot para rollback se falhar
        memoria_backup = dict(self.memoria)
        mensagens_locais: list[str] = []

        try:
            # Executa instruções
            for inst in op.instrucoes_ctx:
                self._executar_instrucao(inst, mensagens_locais)

            # Reavalia marcos em cascata
            marcos_novos = self.reavaliar_marcos_e_progresso()
            self.historico_narracao.extend(mensagens_locais)

            return RespostaOperacao(
                sucesso=True,
                motivo="Operação aplicada com sucesso.",
                mensagens_narradas=mensagens_locais,
                marcos_concluidos_nesta_rodada=marcos_novos,
                historia_encerrada=self.historia_encerrada,
            )
        except Exception as e:
            # Rollback
            self.memoria = memoria_backup
            return RespostaOperacao(
                sucesso=False,
                motivo=f"Erro durante execução da operação: {e}",
            )

    def _executar_instrucao(self, inst_ctx: Any, mensagens: list[str]):
        if inst_ctx.atribuicao():
            atrib = inst_ctx.atribuicao()
            partes = [id_tok.getText() for id_tok in atrib.caminho().IDENT()]
            caminho_fmt = ".".join(partes)
            novo_val = self.avaliar_expressao(atrib.expr())
            self.memoria[caminho_fmt] = novo_val

        elif inst_ctx.comando_narrar():
            msg = self.avaliar_expressao(inst_ctx.comando_narrar().expr())
            mensagens.append(str(msg))

        elif inst_ctx.comando_se():
            se_ctx = inst_ctx.comando_se()
            cond = bool(self.avaliar_expressao(se_ctx.expr()))
            blocos = se_ctx.bloco_instrucoes()
            if cond and len(blocos) > 0:
                for sub_inst in blocos[0].instrucao_operacao():
                    self._executar_instrucao(sub_inst, mensagens)
            elif not cond and len(blocos) > 1:
                # senao
                for sub_inst in blocos[1].instrucao_operacao():
                    self._executar_instrucao(sub_inst, mensagens)

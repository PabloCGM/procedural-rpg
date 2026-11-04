"""Testes automatizados da Execução e Runtime (E4)."""

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.analise_sintatica import analisar_sintaxe
from src.analise_semantica import analisar_semantica
from src.interpretador import MotorExecucaoRPG


class ExecucaoRuntimeTests(unittest.TestCase):
    def test_execucao_ola_ml(self):
        caminho = Path("exemplos/ola.ml")
        texto = caminho.read_text(encoding="utf-8-sig")
        res_sint = analisar_sintaxe(texto)
        res_sem = analisar_semantica(res_sint.arvore)
        self.assertTrue(res_sem.sucesso)

        motor = MotorExecucaoRPG(res_sem, res_sint.arvore)

        # Estado inicial
        self.assertEqual(motor.memoria.get("ola.estado.cumprimentou"), False)
        self.assertFalse(motor.status_marcos["saudacao"])
        self.assertFalse(motor.historia_encerrada)

        # Operação habilitada
        disp = motor.obter_operacoes_disponiveis()
        self.assertIn("ola.cumprimentar", disp)

        # Executa operação
        resp = motor.executar_operacao("ola.cumprimentar")
        self.assertTrue(resp.sucesso)
        self.assertIn("Olá, mundo!", resp.mensagens_narradas)
        self.assertIn("saudacao", resp.marcos_concluidos_nesta_rodada)
        self.assertTrue(resp.historia_encerrada)

        # Após encerrar, nenhuma operação disponível
        self.assertEqual(motor.obter_operacoes_disponiveis(), [])

    def test_execucao_espiral_ml(self):
        caminho = Path("exemplos/espiral.ml")
        texto = caminho.read_text(encoding="utf-8-sig")
        res_sint = analisar_sintaxe(texto)
        res_sem = analisar_semantica(res_sint.arvore)
        self.assertTrue(res_sem.sucesso)

        motor = MotorExecucaoRPG(res_sem, res_sint.arvore)

        # Estado inicial
        self.assertEqual(motor.memoria.get("espiral.estado.volta"), 0)
        self.assertEqual(motor.memoria.get("espiral.estado.raio"), 16.0)
        self.assertFalse(motor.status_marcos["primeira"])

        # Desce uma volta
        resp = motor.executar_operacao("espiral.descer_uma_volta")
        self.assertTrue(resp.sucesso)
        self.assertEqual(motor.memoria.get("espiral.estado.volta"), 1)
        self.assertEqual(motor.memoria.get("espiral.estado.raio"), 8.0)

        # Marco 'primeira' e 'metade' devem ter sido concluídos
        self.assertTrue(motor.status_marcos["primeira"])
        self.assertTrue(motor.status_marcos["metade"])

    def test_cli_execucao_com_script(self):
        cmd = [
            sys.executable,
            str(RAIZ / "src/executar.py"),
            "--script",
            str(RAIZ / "tests/roteiro_ola.txt"),
            "exemplos/ola.ml",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")
        self.assertEqual(res.returncode, 0)
        self.assertIn("SESSÃO DE RPG INICIADA", res.stdout)
        self.assertIn("Olá, mundo!", res.stdout)
        self.assertIn("MARCO CONCLUÍDO]: saudacao", res.stdout)


if __name__ == "__main__":
    unittest.main()

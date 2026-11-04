"""Testes automatizados da Análise Semântica (E4)."""

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.analise_sintatica import analisar_sintaxe
from src.analise_semantica import analisar_semantica


class SemanticoValidosTests(unittest.TestCase):
    """Garante que todos os programas válidos passam na análise semântica."""

    def test_exemplos_validos_passam_semantica(self):
        pasta = Path("exemplos")
        for caminho in sorted(pasta.glob("*.ml")):
            with self.subTest(arquivo=caminho.name):
                texto = caminho.read_text(encoding="utf-8-sig")
                res_sint = analisar_sintaxe(texto)
                self.assertEqual(res_sint.erros, [], f"{caminho.name} falhou na sintaxe.")
                res_sem = analisar_semantica(res_sint.arvore)
                self.assertEqual(
                    res_sem.erros,
                    [],
                    f"{caminho.name} gerou erros semânticos inesperados: {[e.formatar() if hasattr(e, 'formatar') else e.mensagem for e in res_sem.erros]}",
                )
                self.assertTrue(res_sem.sucesso)


class SemanticoInvalidosTests(unittest.TestCase):
    """Garante que programas com erros semânticos são devidamente rejeitados."""

    def test_invalidos_semanticos_sao_rejeitados(self):
        casos = [
            ("tipo_incompativel_soma.ml", "tipos incompatíveis para operador '+'"),
            ("tipo_incompativel_atribuicao.ml", "atribuição de tipo incompatível"),
            ("variavel_nao_declarada.ml", "inexistente ou inacessível"),
            ("metodo_receptor_invalido.ml", "não possui método de criação"),
            ("ciclo_dependencia_marcos.ml", "dependência cíclica detectada"),
            ("historia_de_outra_campanha.ml", "não pertence à campanha"),
            ("operacao_sem_booleano_requer.ml", "cláusula 'requer' exige expressão do tipo 'booleano'"),
        ]

        pasta = Path("invalidos")
        for nome_arq, msg_esperada in casos:
            caminho = pasta / nome_arq
            self.assertTrue(caminho.exists(), f"Arquivo de teste {nome_arq} não existe.")
            with self.subTest(arquivo=nome_arq):
                texto = caminho.read_text(encoding="utf-8-sig")
                res_sint = analisar_sintaxe(texto)
                self.assertEqual(res_sint.erros, [], f"{nome_arq} deveria passar no sintático para testar semântica.")
                res_sem = analisar_semantica(res_sint.arvore)
                self.assertFalse(res_sem.sucesso, f"{nome_arq} deveria falhar na semântica, mas passou.")
                mensagens = " | ".join(e.mensagem for e in res_sem.erros)
                self.assertIn(
                    msg_esperada,
                    mensagens,
                    f"Erro esperado '{msg_esperada}' não encontrado em: {mensagens}",
                )


class CLISemanticoTests(unittest.TestCase):
    def executar_cli(self, *args):
        cmd = [sys.executable, str(RAIZ / "src/executar.py"), *args]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")

    def test_cli_apenas_semantico_sucesso(self):
        res = self.executar_cli("--apenas-semantico", "exemplos/ola.ml")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Sucesso semântico", res.stdout)

    def test_cli_apenas_semantico_erro(self):
        res = self.executar_cli("--apenas-semantico", "invalidos/tipo_incompativel_soma.ml")
        self.assertEqual(res.returncode, 1)
        self.assertIn("tipos incompatíveis para operador '+'", res.stderr)


if __name__ == "__main__":
    unittest.main()

"""Testes do módulo de visualização, tradução de mensagens e pipeline da interface."""

from pathlib import Path
import unittest

from src.analise_sintatica import analisar_sintaxe
from src.visualizacao.mensagens import traduzir_mensagem_antlr
from src.visualizacao.modelo import construir_modelo_dados


class MensagensTraducaoTests(unittest.TestCase):
    def test_traduz_extraneous_input(self):
        msg = "extraneous input '*' expecting {'verdadeiro', 'falso', IDENT}"
        traduzida, orig = traduzir_mensagem_antlr(msg)
        self.assertEqual(orig, msg)
        self.assertIn("está sobrando aqui", traduzida)
        self.assertIn("'*'", traduzida)

    def test_traduz_mismatched_input(self):
        msg = "mismatched input 'narrar' expecting 'requer'"
        traduzida, orig = traduzir_mensagem_antlr(msg)
        self.assertIn("encontrei", traduzida)
        self.assertIn("esperava 'requer'", traduzida)

    def test_traduz_missing(self):
        msg = "missing ')' at '\\n'"
        traduzida, _ = traduzir_mensagem_antlr(msg)
        self.assertIn("faltou ')'", traduzida)

    def test_traduz_no_viable_alternative(self):
        msg = "no viable alternative at input 'x'"
        traduzida, _ = traduzir_mensagem_antlr(msg)
        self.assertIn("não reconheci nenhuma construção gramatical válida", traduzida)

    def test_mensagem_desconhecida_mantem_original(self):
        msg = "custom error without standard pattern"
        traduzida, orig = traduzir_mensagem_antlr(msg)
        self.assertEqual(traduzida, msg)
        self.assertEqual(orig, msg)


class PipelineParadaPreventivaTests(unittest.TestCase):
    def test_arquivo_invalido_lexico_bloqueia_parser_sem_erros_falsos(self):
        # invalidos/numero_malformado.ml tem apenas 1 erro léxico verdadeiro (.5)
        caminho = Path("invalidos/numero_malformado.ml")
        texto = caminho.read_text(encoding="utf-8")
        resultado = analisar_sintaxe(texto, parar_em_erro_lexico=True)

        self.assertTrue(resultado.bloqueado)
        self.assertIsNone(resultado.arvore)
        self.assertIsNone(resultado.parser)
        # Deve ter apenas o erro léxico verdadeiro, sem erros sintáticos em cascata!
        self.assertEqual(len(resultado.erros), 1)
        self.assertEqual(resultado.erros[0].categoria, "léxico")

    def test_arquivo_valido_executa_parser_completamente(self):
        caminho = Path("exemplos/ola.ml")
        texto = caminho.read_text(encoding="utf-8")
        resultado = analisar_sintaxe(texto, parar_em_erro_lexico=True)

        self.assertFalse(resultado.bloqueado)
        self.assertIsNotNone(resultado.arvore)
        self.assertEqual(resultado.erros, [])


class ModeloDadosTests(unittest.TestCase):
    def test_modelo_ola_ml(self):
        caminho = Path("exemplos/ola.ml")
        texto = caminho.read_text(encoding="utf-8")
        resultado = analisar_sintaxe(texto)
        modelo = construir_modelo_dados(str(caminho), texto, resultado)

        self.assertEqual(modelo["arquivo"], str(caminho))
        self.assertEqual(len(modelo["tokens"]), 197)
        self.assertEqual(len(modelo["fases"]), 4)
        self.assertEqual(modelo["fases"][0]["status"], "ok")
        self.assertEqual(modelo["fases"][1]["status"], "ok")
        self.assertEqual(modelo["arvore"]["nome"], "programa")
        self.assertIsInstance(modelo["arvore"]["filhos"], list)
        self.assertGreater(len(modelo["arvore"]["filhos"]), 0)


if __name__ == "__main__":
    unittest.main()

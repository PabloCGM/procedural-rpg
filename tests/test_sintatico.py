"""Testes automatizados da análise sintática e árvore sintática (E3)."""

from pathlib import Path
import subprocess
import sys
import unittest

from src.analise_sintatica import analisar_sintaxe


class ExemplosValidosSintaticoTests(unittest.TestCase):
    def test_exemplos_validos_passam_sem_erros(self):
        exemplos = ["ola.ml", "quadrado.ml", "espiral.ml", "parte_a.ml"]
        for nome in exemplos:
            caminho = Path("exemplos") / nome
            with self.subTest(arquivo=nome):
                texto = caminho.read_text(encoding="utf-8-sig")
                resultado = analisar_sintaxe(texto)
                self.assertEqual(
                    resultado.erros,
                    [],
                    f"{nome} produziu erros sintáticos inesperados: {resultado.erros}",
                )
                self.assertIsNotNone(resultado.arvore)


class ExemplosInvalidosSintaticoTests(unittest.TestCase):
    def test_invalidos_sintaticos_sao_rejeitados(self):
        pasta = Path("invalidos_sintaticos")
        arquivos = list(pasta.glob("*.ml"))
        self.assertGreaterEqual(len(arquivos), 5)
        for caminho in arquivos:
            with self.subTest(arquivo=caminho.name):
                texto = caminho.read_text(encoding="utf-8-sig")
                resultado = analisar_sintaxe(texto)
                self.assertGreater(
                    len(resultado.erros),
                    0,
                    f"{caminho.name} deveria falhar na sintaxe, mas passou sem erros.",
                )


class PrecedenciaArvoreTests(unittest.TestCase):
    def test_multiplicacao_tem_precedencia_sobre_soma(self):
        # 2 + 3 * 4 -> o nó raiz da expressão deve ser aditiva (soma)
        codigo = (
            'vila = Universo("vila")\n'
            '    inteiro vila.estado.x = 2 + 3 * 4\n'
            'jornada = vila.campanhas.jornada\n'
            'iniciar jornada com jornada.historias.ola\n'
        )
        resultado = analisar_sintaxe(codigo)
        self.assertEqual(resultado.erros, [])
        # Inspeciona a representação em S-expression do ANTLR
        tree_str = resultado.arvore.toStringTree(recog=resultado.parser)
        # Na árvore: (+ 2 (* 3 4))
        self.assertIn('+ (expr (expr (literal 3)) * (expr (literal 4)))', tree_str)

    def test_parenteses_alteram_precedencia(self):
        # (2 + 3) * 4 -> o nó raiz da expressão deve ser multiplicativa (*)
        codigo = (
            'vila = Universo("vila")\n'
            '    inteiro vila.estado.x = (2 + 3) * 4\n'
            'jornada = vila.campanhas.jornada\n'
            'iniciar jornada com jornada.historias.ola\n'
        )
        resultado = analisar_sintaxe(codigo)
        self.assertEqual(resultado.erros, [])
        tree_str = resultado.arvore.toStringTree(recog=resultado.parser)
        self.assertIn('* (expr (literal 4))', tree_str)
        self.assertIn('(expr (literal 2)) + (expr (literal 3))', tree_str)


class CLISintaticoTests(unittest.TestCase):
    def executar_cli(self, *args):
        cmd = [sys.executable, "src/sintatico.py", *args]
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_cli_sucesso(self):
        res = self.executar_cli("exemplos/ola.ml")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Sucesso sintático", res.stdout)

    def test_cli_com_flag_arvore(self):
        res = self.executar_cli("--arvore", "exemplos/ola.ml")
        self.assertEqual(res.returncode, 0)
        self.assertIn("ÁRVORE SINTÁTICA CONCRETA", res.stdout)
        self.assertIn("Programa", res.stdout)

    def test_cli_erro_sintatico_retorna_um(self):
        res = self.executar_cli("invalidos_sintaticos/parenteses_sem_fechar.ml")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Erro sintático", res.stderr)

    def test_cli_arquivo_inexistente_retorna_dois(self):
        res = self.executar_cli("arquivo_fantasma.ml")
        self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()

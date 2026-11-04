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


class EstruturaNarrativaTests(unittest.TestCase):
    def test_extrai_estrutura_ola_ml(self):
        from src.visualizacao.estrutura import extrair_estrutura_narrativa

        caminho = Path("exemplos/ola.ml")
        texto = caminho.read_text(encoding="utf-8")
        resultado = analisar_sintaxe(texto)
        estrutura = extrair_estrutura_narrativa(resultado.arvore, texto)

        # Entidades principais
        self.assertEqual(len(estrutura["entidades"]), 1)
        universo = estrutura["entidades"][0]
        self.assertEqual(universo["variavel"], "vila")
        self.assertEqual(universo["tipo"], "universo")
        self.assertEqual(universo["propriedades"].get("nome"), "Vila do Início")

        # Campanha filha
        self.assertEqual(len(universo["filhos"]), 1)
        campanha = universo["filhos"][0]
        self.assertEqual(campanha["variavel"], "jornada")
        self.assertEqual(campanha["tipo"], "campanha")

        # Marcos
        marcos = {m["variavel"]: m for m in estrutura["marcos"]}
        self.assertIn("saudacao", marcos)
        self.assertEqual(marcos["saudacao"]["condicao"], "ola.estado.cumprimentou")

        # Operações
        self.assertEqual(len(estrutura["operacoes"]), 1)
        op = estrutura["operacoes"][0]
        self.assertEqual(op["caminho"], "ola.cumprimentar")
        self.assertIn("nao ola.estado.cumprimentou", op["requer"])

        # Iniciar
        self.assertIsNotNone(estrutura["iniciar"])
        self.assertEqual(estrutura["iniciar"]["campanha"], "jornada")

    def test_extrai_dependencias_espiral_ml(self):
        from src.visualizacao.estrutura import extrair_estrutura_narrativa

        caminho = Path("exemplos/espiral.ml")
        texto = caminho.read_text(encoding="utf-8")
        resultado = analisar_sintaxe(texto)
        estrutura = extrair_estrutura_narrativa(resultado.arvore, texto)

        marcos = {m["variavel"]: m for m in estrutura["marcos"]}
        self.assertIn("primeira", marcos)
        self.assertIn("metade", marcos)
        self.assertIn("fundo", marcos)
        self.assertIn("primeira", marcos["metade"]["dependencias"])
        self.assertIn("metade", marcos["fundo"]["dependencias"])


class HTMLVisualizadorTests(unittest.TestCase):
    def test_gerar_html_seguranca_injecao(self):
        import json
        from src.visualizacao.html import gerar_html_visualizador

        # Teste de payload malicioso contendo </script>
        modelo_teste = {
            "arquivo": "teste.ml",
            "fonte": 'texto x = "</script><script>alert(1)</script>"',
            "fases": [],
            "tokens": [],
            "erros": [],
            "arvore": None,
            "estrutura": {},
        }
        html = gerar_html_visualizador(modelo_teste)

        # Não deve haver </script> solto dentro do script de dados
        self.assertNotIn('</script><script>alert(1)</script>', html)
        self.assertIn(r'\u003c/script>', html)

    def test_html_contem_recursos_pan_zoom_diagrama(self):
        from src.visualizacao.html import gerar_html_visualizador

        modelo_teste = {
            "arquivo": "ola.ml",
            "fonte": 'mundo = Universo("vila")',
            "fases": [],
            "tokens": [],
            "erros": [],
            "arvore": {"id": 1, "nome": "programa", "tipo": "regra", "linha_inicio": 1, "coluna_inicio": 0, "linha_fim": 1, "coluna_fim": 23, "filhos": []},
            "estrutura": {},
        }
        html = gerar_html_visualizador(modelo_teste)

        # Verifica presença dos elementos essenciais de pan e zoom
        self.assertIn('btn-zoom-mais', html)
        self.assertIn('btn-zoom-menos', html)
        self.assertIn('zoom-indicador', html)
        self.assertIn('btn-zoom-ajustar', html)
        self.assertIn('diagrama-canvas-area', html)
        self.assertIn('diagrama-viewport', html)



class CLIVisualizarTests(unittest.TestCase):
    def executar_cli(self, *args):
        import subprocess
        import sys
        cmd = [sys.executable, "src/visualizar.py", *args]
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_cli_sucesso_gera_arquivo(self):
        saida_teste = Path("visualizacoes/teste_ola.html")
        if saida_teste.exists():
            saida_teste.unlink()

        res = self.executar_cli("exemplos/ola.ml", "--saida", str(saida_teste), "--nao-abrir")
        self.assertEqual(res.returncode, 0)
        self.assertTrue(saida_teste.exists())
        self.assertGreater(saida_teste.stat().st_size, 1000)

        # Limpeza
        if saida_teste.exists():
            saida_teste.unlink()

    def test_cli_erro_gera_arquivo_com_codigo_um(self):
        saida_teste = Path("visualizacoes/teste_invalido.html")
        if saida_teste.exists():
            saida_teste.unlink()

        res = self.executar_cli("invalidos/parenteses_sem_fechar.ml", "--saida", str(saida_teste), "--nao-abrir")
        self.assertEqual(res.returncode, 1)
        self.assertTrue(saida_teste.exists())

        # Limpeza
        if saida_teste.exists():
            saida_teste.unlink()

    def test_cli_arquivo_inexistente_retorna_dois(self):
        res = self.executar_cli("arquivo_fantasma.ml", "--nao-abrir")
        self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()



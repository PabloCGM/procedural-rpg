"""Casos de reconhecimento, recuperação de erros, layout e interface de linha de comando."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.analise_lexica import analisar, nome_token


RAIZ = Path(__file__).resolve().parents[1]
LAYOUT = {"NOVA_LINHA", "INDENTA", "DEDENTA"}


def conteudo(resultado):
    return [(nome_token(t), t.text) for t in resultado.tokens if nome_token(t) not in LAYOUT]


class ReconhecimentoTests(unittest.TestCase):
    def test_palavras_reservadas_e_limites(self):
        palavras = (
            "inteiro real texto booleano verdadeiro falso concluir quando encerrar "
            "operacao requer iniciar com narrar se senao e ou nao"
        )
        esperado = (
            "TIPO_INTEIRO TIPO_REAL TIPO_TEXTO TIPO_BOOLEANO VERDADEIRO FALSO "
            "CONCLUIR QUANDO ENCERRAR OPERACAO REQUER INICIAR COM NARRAR SE SENAO E OU NAO"
        ).split()
        resultado = analisar(palavras)
        self.assertFalse(resultado.erros)
        self.assertEqual([tipo for tipo, _ in conteudo(resultado)], esperado)
        self.assertEqual(
            conteudo(analisar("Universo iniciar_sessao inteiro2 _nome Se personagem")),
            [("IDENT", s) for s in "Universo iniciar_sessao inteiro2 _nome Se personagem".split()],
        )

    def test_operadores_e_delimitadores(self):
        resultado = analisar("== != <= >= = < > + - * / . ( ) ,")
        self.assertFalse(resultado.erros)
        self.assertEqual(
            [tipo for tipo, _ in conteudo(resultado)],
            "IGUAL DIFERENTE MENOR_IGUAL MAIOR_IGUAL ATRIBUICAO MENOR MAIOR MAIS MENOS "
            "MULTIPLICACAO DIVISAO PONTO ABRE_PAREN FECHA_PAREN VIRGULA".split(),
        )

    def test_numeros_sinais_e_acesso_por_ponto(self):
        resultado = analisar("-12 +0 0.5 12.75 mundo.personagens.helena")
        self.assertFalse(resultado.erros)
        self.assertEqual(conteudo(resultado), [
            ("MENOS", "-"), ("INTEIRO", "12"), ("MAIS", "+"), ("INTEIRO", "0"),
            ("REAL", "0.5"), ("REAL", "12.75"), ("IDENT", "mundo"), ("PONTO", "."),
            ("IDENT", "personagens"), ("PONTO", "."), ("IDENT", "helena"),
        ])

    def test_textos_unicode_escapes_e_barras(self):
        for literal in ['""', '"Memórias 🐉"', r'"a\"b\\c\nd\t"', '"https://exemplo"', '"a\tb"']:
            with self.subTest(literal=literal):
                resultado = analisar(literal)
                self.assertFalse(resultado.erros)
                self.assertEqual(conteudo(resultado), [("TEXTO", literal)])

    def test_comentarios_espacos_e_divisao(self):
        resultado = analisar('// comentario\nvalor = 6 / 2 // ignorar @ e "\n')
        self.assertFalse(resultado.erros)
        self.assertEqual(conteudo(resultado), [
            ("IDENT", "valor"), ("ATRIBUICAO", "="), ("INTEIRO", "6"),
            ("DIVISAO", "/"), ("INTEIRO", "2"),
        ])
        self.assertEqual(resultado.tokens[0].line, 2)

    def test_exemplo_completo_da_parte_a(self):
        documento = (RAIZ / "docs/especificacao.md").read_text(encoding="utf-8")
        codigo = documento.split("```text\n", 1)[1].split("\n```", 1)[0]
        resultado = analisar(codigo)
        self.assertFalse(resultado.erros)
        nomes = [nome_token(t) for t in resultado.tokens]
        self.assertIn("OPERACAO", nomes)
        self.assertEqual(nomes.count("INICIAR"), 1)
        self.assertEqual(nomes.count("INDENTA"), nomes.count("DEDENTA"))

    def test_lexer_nao_faz_analise_semantica_ou_sintatica(self):
        # Tokens válidos, embora não seja um programa sintaticamente correto.
        resultado = analisar("iniciar + desconhecido(\n    foo\n")
        self.assertFalse(resultado.erros)


class DiagnosticosTests(unittest.TestCase):
    def test_numeros_malformados_nao_sao_fragmentados_em_tokens_validos(self):
        for numero in ["3.", ".5", "1.2.3", "12abc", "1e3", "1_000", "0.5x", "1..2"]:
            with self.subTest(numero=numero):
                resultado = analisar("x = " + numero)
                self.assertEqual(len(resultado.erros), 1)
                erro = resultado.erros[0]
                self.assertEqual((erro.linha, erro.coluna), (1, 5))
                self.assertIn("número malformado", erro.mensagem)
                self.assertEqual(conteudo(resultado), [("IDENT", "x"), ("ATRIBUICAO", "=")])

    def test_texto_sem_fechar_recupera_na_linha_seguinte(self):
        resultado = analisar('nome = "sem fechar\nnarrar "ok"')
        self.assertEqual(len(resultado.erros), 1)
        self.assertEqual((resultado.erros[0].linha, resultado.erros[0].coluna), (1, 8))
        self.assertEqual(conteudo(resultado)[-2:], [("NARRAR", "narrar"), ("TEXTO", '"ok"')])

    def test_texto_sem_fechar_no_eof_com_escape(self):
        for literal in ['"', '"abc', '"abc\\', '"abc\\"']:
            with self.subTest(literal=literal):
                resultado = analisar(literal)
                self.assertEqual(len(resultado.erros), 1)
                self.assertEqual(resultado.erros[0].mensagem, "texto sem fechar")

    def test_escape_invalido_aponta_a_barra(self):
        resultado = analisar(r'"abc\q"')
        self.assertEqual(len(resultado.erros), 1)
        self.assertEqual(resultado.erros[0].coluna, 5)
        self.assertIn("escape inválido", resultado.erros[0].mensagem)

    def test_caractere_invalido_com_linha_e_coluna(self):
        resultado = analisar("x = 1\ny = @")
        self.assertEqual(len(resultado.erros), 1)
        self.assertEqual((resultado.erros[0].linha, resultado.erros[0].coluna), (2, 5))

    def test_multiplos_erros_e_recuperacao(self):
        resultado = analisar('@ 12abc "x\\q"\niniciar campanha com historia')
        self.assertEqual(len(resultado.erros), 3)
        self.assertIn(("INICIAR", "iniciar"), conteudo(resultado))

    def test_tabulacao_fora_de_texto(self):
        resultado = analisar("nome\t= 1")
        self.assertEqual(len(resultado.erros), 1)
        self.assertEqual(resultado.erros[0].coluna, 5)
        self.assertIn("tabulação", resultado.erros[0].mensagem)


class LayoutTests(unittest.TestCase):
    def test_arvore_e_fechamento_no_eof_sem_quebra_final(self):
        resultado = analisar("raiz\n    filho\n        neto\n    irmao")
        self.assertFalse(resultado.erros)
        self.assertEqual([nome_token(t) for t in resultado.tokens], [
            "IDENT", "NOVA_LINHA", "INDENTA", "IDENT", "NOVA_LINHA", "INDENTA",
            "IDENT", "NOVA_LINHA", "DEDENTA", "IDENT", "NOVA_LINHA", "DEDENTA",
        ])

    def test_linhas_vazias_e_comentarios_nao_alteram_layout(self):
        resultado = analisar("raiz\n // comentario com recuo irregular\n\n    filho\n// fim\n")
        self.assertFalse(resultado.erros)
        self.assertEqual([nome_token(t) for t in resultado.tokens], [
            "IDENT", "NOVA_LINHA", "INDENTA", "IDENT", "NOVA_LINHA", "DEDENTA",
        ])

    def test_arquivo_vazio_ou_so_comentarios(self):
        for texto in ["", "\n   \n", "// comentario", "    // comentario\n"]:
            with self.subTest(texto=texto):
                resultado = analisar(texto)
                self.assertFalse(resultado.erros)
                self.assertEqual(resultado.tokens, [])

    def test_recuos_invalidos(self):
        for texto, posicao in [
            ("    raiz", (1, 5)),
            ("raiz\n  filho", (2, 3)),
            ("raiz\n        neto", (2, 9)),
            ("raiz\n    filho\n        neto\n      ruim", (4, 7)),
        ]:
            with self.subTest(texto=texto):
                resultado = analisar(texto)
                self.assertEqual(len(resultado.erros), 1)
                self.assertEqual((resultado.erros[0].linha, resultado.erros[0].coluna), posicao)

    def test_crlf_cr_e_bom_preservam_linhas(self):
        for quebra in ["\n", "\r\n", "\r"]:
            with self.subTest(quebra=quebra):
                resultado = analisar("\ufeffraiz" + quebra + "    filho" + quebra)
                self.assertFalse(resultado.erros)
                filho = next(t for t in resultado.tokens if t.text == "filho")
                self.assertEqual((filho.line, filho.column + 1), (2, 5))


class ExemplosTests(unittest.TestCase):
    """Parte C: programas válidos e inválidos entregues em exemplos/ e invalidos/."""

    def ler(self, caminho):
        return (RAIZ / caminho).read_text(encoding="utf-8-sig")

    def test_exemplos_validos_sem_erros(self):
        for nome in ["ola", "quadrado", "espiral", "parte_a"]:
            with self.subTest(exemplo=nome):
                resultado = analisar(self.ler(f"exemplos/{nome}.ml"))
                self.assertFalse(resultado.erros)
                nomes = [nome_token(t) for t in resultado.tokens]
                self.assertEqual(nomes.count("INICIAR"), 1)
                self.assertEqual(nomes.count("INDENTA"), nomes.count("DEDENTA"))

    def test_parte_a_igual_ao_programa_da_especificacao(self):
        documento = self.ler("docs/especificacao.md")
        codigo = documento.split("```text\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(self.ler("exemplos/parte_a.ml").rstrip("\n"), codigo)

    def test_invalidos_localizam_o_erro(self):
        for nome, posicao, mensagem in [
            ("caractere_invalido", (6, 38), "caractere não reconhecido: ';'"),
            ("texto_sem_fechar", (6, 17), "texto sem fechar"),
            ("numero_malformado", (7, 30), "número malformado: '.5'"),
        ]:
            with self.subTest(invalido=nome):
                resultado = analisar(self.ler(f"invalidos/{nome}.ml"))
                self.assertEqual(len(resultado.erros), 1)
                erro = resultado.erros[0]
                self.assertEqual((erro.linha, erro.coluna), posicao)
                self.assertEqual(erro.mensagem, mensagem)


class CLITests(unittest.TestCase):
    def rodar(self, texto):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "programa.ml"
            arquivo.write_text(texto, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(RAIZ / "src/lexico.py"), str(arquivo)],
                cwd=pasta, capture_output=True, encoding="utf-8", check=False,
            )

    def test_saida_e_contagem_incluem_layout_mas_nao_eof(self):
        saida = self.rodar("iniciar campanha com historia\n")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("INICIAR 'iniciar' linha 1 coluna 1", saida.stdout)
        self.assertIn("5 tokens reconhecidos", saida.stdout)
        self.assertNotIn("EOF", saida.stdout)
        self.assertEqual(saida.stderr, "")

    def test_erro_no_stderr_e_codigo_um(self):
        saida = self.rodar("nome = @")
        self.assertEqual(saida.returncode, 1)
        self.assertIn("linha 1, coluna 8", saida.stderr)
        self.assertNotIn("CARACTERE_INVALIDO", saida.stdout)

    def test_arquivo_inexistente_retorna_dois(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = subprocess.run(
                [sys.executable, str(RAIZ / "src/lexico.py"), str(Path(pasta) / "ausente.ml")],
                capture_output=True, encoding="utf-8", check=False,
            )
        self.assertEqual(saida.returncode, 2)
        self.assertIn("Erro ao ler", saida.stderr)


if __name__ == "__main__":
    unittest.main()

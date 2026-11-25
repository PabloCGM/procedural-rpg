"""CLI principal de execução e simulador de sessão RPG (E4)."""

import argparse
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.analise_sintatica import analisar_sintaxe, formatar_arvore
from src.analise_semantica import analisar_semantica
from src.interpretador import MotorExecucaoRPG


def executar_pipeline(caminho: Path, apenas_semantico: bool = False, arvore_flag: bool = False, script_caminho: Path | None = None) -> int:
    if not caminho.exists():
        sys.stderr.write(f"Erro: arquivo '{caminho}' não encontrado.\n")
        return 2

    texto = caminho.read_text(encoding="utf-8-sig")

    # 1. Análise Léxica e Sintática (E2 e E3)
    res_sint = analisar_sintaxe(texto)
    if res_sint.erros:
        for erro in res_sint.erros:
            sys.stderr.write(f"linha {erro.linha}, coluna {erro.coluna}: {erro.mensagem}\n")
        return 1

    # 2. Análise Semântica (E4)
    res_sem = analisar_semantica(res_sint.arvore)
    if res_sem.erros:
        for erro in res_sem.erros:
            sys.stderr.write(f"linha {erro.linha}, coluna {erro.coluna}: {erro.mensagem}\n")
        return 1

    if arvore_flag and res_sint.arvore:
        print("--- ÁRVORE SINTÁTICA CONCRETA ---")
        print(formatar_arvore(res_sint.arvore, res_sint.parser))
        print("---------------------------------\n")

    if apenas_semantico:
        print(f"Sucesso semântico: '{caminho}' é válido!")
        return 0

    # 3. Execução / Runtime (E4)
    motor = MotorExecucaoRPG(res_sem, res_sint.arvore)
    print("======================================================================")
    print(f"SESSÃO DE RPG INICIADA: {res_sem.campanha_iniciar} (História: {res_sem.historia_iniciar})")
    print("======================================================================")

    # Modo Script (comandos automáticos de arquivo)
    if script_caminho:
        if not script_caminho.exists():
            sys.stderr.write(f"Erro: script '{script_caminho}' não encontrado.\n")
            return 2
        comandos = [l.strip() for l in script_caminho.read_text(encoding="utf-8").splitlines() if l.strip()]
        for cmd in comandos:
            print(f"\n[COMANDO]: {cmd}")
            resp = motor.executar_operacao(cmd)
            _exibir_resposta(resp)
            if resp.historia_encerrada:
                break
        return 0

    # Modo Interativo via Terminal
    while not motor.historia_encerrada:
        print("\n--- Estado Atual ---")
        for k, v in motor.memoria.items():
            if not k.endswith(".concluido"):
                print(f"  • {k} = {_formatar_valor(v)}")

        print("\nMarcos:")
        for m, status in motor.status_marcos.items():
            st_str = "[X]" if status else "[ ]"
            print(f"  {st_str} {m}")

        ops = motor.obter_operacoes_disponiveis()
        print("\nOperações Habilitadas:")
        if not ops:
            print("  (Nenhuma operação habilitada no momento)")
            break

        for idx, op in enumerate(ops, 1):
            print(f"  [{idx}] {op}")
        print("  [0] Sair da sessão")

        try:
            escolha = input("\nEscolha a operação: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSessão interrompida pelo usuário.")
            return 0

        if escolha in ("0", "sair", "exit"):
            print("Sessão finalizada.")
            return 0

        if escolha.isdigit() and 1 <= int(escolha) <= len(ops):
            op_escolhida = ops[int(escolha) - 1]
            print(f"\n>>> Disparando operação: {op_escolhida}...")
            resp = motor.executar_operacao(op_escolhida)
            _exibir_resposta(resp)
        else:
            print("Opção inválida. Tente novamente.")

    if motor.historia_encerrada:
        print("\n[HISTÓRIA ENCERRADA COM SUCESSO! Parabéns!]")

    return 0


def _formatar_valor(valor) -> str:
    """Mostra o valor com a grafia da linguagem (verdadeiro/falso, texto entre aspas)."""
    if isinstance(valor, bool):
        return "verdadeiro" if valor else "falso"
    if isinstance(valor, str):
        return f'"{valor}"'
    return str(valor)


def _exibir_resposta(resp):
    if resp.sucesso:
        for msg in resp.mensagens_narradas:
            print(f"  [NARRAR]: \"{msg}\"")
        for m in resp.marcos_concluidos_nesta_rodada:
            print(f"  [MARCO CONCLUÍDO]: {m}")
        if resp.historia_encerrada:
            print("  [STATUS]: Condição de encerramento da história satisfeita!")
    else:
        print(f"  [FALHA]: {resp.motivo}")


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Compilador e Interpretador de Procedural RPG (E4).")
    parser.add_argument("arquivo", type=Path, help="Caminho do programa fonte (.ml).")
    parser.add_argument("--apenas-semantico", action="store_true", help="Valida apenas a análise semântica sem rodar a sessão.")
    parser.add_argument("--arvore", action="store_true", help="Exibe a árvore sintática concreta.")
    parser.add_argument("--script", type=Path, default=None, help="Executa comandos em lote de um arquivo texto.")

    args = parser.parse_args()
    return executar_pipeline(args.arquivo, args.apenas_semantico, args.arvore, args.script)


if __name__ == "__main__":
    sys.exit(main())

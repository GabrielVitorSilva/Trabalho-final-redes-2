"""Exercicio 4 - Cliente de hora.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Torna possível reutilizar o módulo common.py na raiz.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, fechar_socket_sem_erro, enviar_linha


def pedir_hora(conexao: socket.socket) -> str | None:
    """Envia o pedido de hora e retorna a resposta."""
    # Envia uma solicitação textual simples para o servidor.
    enviar_linha(conexao, "hora")
    leitor = conexao.makefile("r", encoding="utf-8", newline="\n")
    try:
        # Lê a resposta única contendo a hora formatada.
        resposta = leitor.readline().rstrip("\r\n")
        return resposta or None
    finally:
        # Fecha o leitor logo após a resposta ser consumida.
        leitor.close()


def executar_cliente(host: str, port: int, uma_vez: bool) -> None:
    """Conecta no servidor de hora e faz os pedidos."""
    print(cabecalho_projeto("Exercicio 4 - Cliente de Hora"))
    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Abre a conexão com o servidor multithread.
        conexao.connect((host, port))

        if uma_vez:
            # Modo simples, pensado para testes rápidos.
            resposta = pedir_hora(conexao)
            print(f"Hora recebida: {resposta if resposta is not None else 'sem resposta'}")
            return

        while True:
            # No modo interativo, o usuário pede novas consultas quando quiser.
            comando = input("Pressione Enter para solicitar a hora ou 'sair' para encerrar: ").strip().lower()
            if comando == "sair":
                break
            resposta = pedir_hora(conexao)
            print(f"Hora recebida: {resposta if resposta is not None else 'sem resposta'}")
    finally:
        # Garante fechamento da conexão em qualquer caminho de saída.
        fechar_socket_sem_erro(conexao)


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Cliente do servidor de hora do Exercicio 4")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7000)
    parser.add_argument("--once", action="store_true", help="Solicita a hora uma unica vez e encerra")
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_cliente(args.host, args.port, args.once)

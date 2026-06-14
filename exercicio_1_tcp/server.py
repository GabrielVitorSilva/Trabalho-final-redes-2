"""Exercicio 1 - Servidor TCP.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import socket
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Adiciona a raiz do projeto para permitir importar common.py.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, enviar_linha, fechar_socket_sem_erro


def atender_cliente(conexao: socket.socket, endereco: tuple[str, int]) -> None:
    """Recebe mensagens de um cliente e confirma cada envio valido."""
    with conexao:
        # Usa um arquivo de texto para ler mensagens linha a linha.
        leitor = conexao.makefile("r", encoding="utf-8", newline="\n")
        try:
            while True:
                # Lê uma linha completa enviada pelo cliente.
                linha = leitor.readline()
                if linha == "":
                    # Conexão encerrada pelo cliente.
                    break

                mensagem = linha.rstrip("\r\n")
                if not mensagem.strip():
                    # A validação evita aceitar mensagens em branco.
                    enviar_linha(conexao, "ERRO: mensagem vazia nao permitida.")
                    continue

                # Exibe no terminal a mensagem recebida para fins de auditoria.
                print(f"[{endereco[0]}:{endereco[1]}] {mensagem}")
                enviar_linha(conexao, "Mensagem recebida")

                if mensagem.strip().lower() == "sair":
                    # Permite que o cliente solicite o encerramento limpo.
                    break
        finally:
            # Fecha o leitor associado ao socket antes de sair da função.
            leitor.close()


def executar_servidor(host: str, port: int) -> None:
    """Inicia o servidor TCP e cria uma thread para cada cliente."""
    print(cabecalho_projeto("Exercicio 1 - Cliente/Servidor TCP"))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Reaproveita a porta rapidamente se o servidor for reiniciado.
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, port))
        servidor.listen()
        print(f"Servidor TCP ouvindo em {host}:{port}")

        try:
            while True:
                # Cada conexão nova ganha sua própria thread de atendimento.
                conexao, endereco = servidor.accept()
                thread = threading.Thread(target=atender_cliente, args=(conexao, endereco), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            # Permite encerrar o processo com Ctrl+C sem traceback.
            print("\nEncerrando servidor TCP.")


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Servidor TCP do Exercicio 1")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_servidor(args.host, args.port)

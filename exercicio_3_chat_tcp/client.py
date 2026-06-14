"""Exercicio 3 - Cliente do chat TCP.

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
    # Permite importar o arquivo common.py da raiz do projeto.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, enviar_linha, fechar_socket_sem_erro


def ler_linha(conexao: socket.socket, sobra: bytes = b"") -> tuple[str | None, bytes]:
    """Le uma linha do socket e devolve o restante do buffer."""
    while b"\n" not in sobra:
        parte = conexao.recv(1024)
        if not parte:
            if sobra:
                return sobra.decode("utf-8", errors="replace").rstrip("\r"), b""
            return None, b""
        sobra += parte

    linha, resto = sobra.split(b"\n", 1)
    return linha.decode("utf-8", errors="replace").rstrip("\r"), resto


def receber_mensagens(conexao: socket.socket, parar: threading.Event) -> None:
    """Fica ouvindo o servidor e imprimindo tudo que chegar."""
    sobra = b""
    try:
        while not parar.is_set():
            linha, sobra = ler_linha(conexao, sobra)
            if linha is None:
                break
            print(linha)
    finally:
        parar.set()


def executar_cliente(host: str, porta: int, nome: str) -> None:
    """Conecta no servidor e permite trocar mensagens."""
    print(cabecalho_projeto("Exercicio 3 - Cliente do Chat TCP"))

    parar = threading.Event()
    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        conexao.connect((host, porta))
        enviar_linha(conexao, nome.strip() or "Anonimo")

        thread_recebimento = threading.Thread(target=receber_mensagens, args=(conexao, parar), daemon=True)
        thread_recebimento.start()

        while not parar.is_set():
            mensagem = input()

            if mensagem.strip().lower() == "sair":
                enviar_linha(conexao, "sair")
                break

            if mensagem.strip() == "":
                print("A mensagem nao pode ser vazia.")
                continue

            enviar_linha(conexao, mensagem)

        parar.set()
        thread_recebimento.join(timeout=2)
    except KeyboardInterrupt:
        parar.set()
    finally:
        fechar_socket_sem_erro(conexao)


def ler_argumentos():
    """Le os argumentos e inicia o cliente."""
    parser = argparse.ArgumentParser(description="Cliente do chat TCP do Exercicio 3")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6500)
    parser.add_argument("--name", default="Participante")
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_cliente(args.host, args.port, args.name)

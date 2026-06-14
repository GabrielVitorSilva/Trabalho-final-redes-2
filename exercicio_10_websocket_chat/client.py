"""Exercicio 10 - Cliente do chat com WebSocket.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import base64
import os
import socket
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Adiciona a raiz do projeto para importar common.py.
    sys.path.insert(0, str(ROOT))

from common import (
    cabecalho_projeto,
    fechar_socket_sem_erro,
    codificar_frame_websocket,
    ler_frame_websocket,
    enviar_fechamento_websocket,
)


def montar_requisicao(host, porta, chave):
    """Monta a requisicao HTTP do handshake."""
    return (
        "GET /chat HTTP/1.1\r\n"
        f"Host: {host}:{porta}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {chave}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    ).encode("utf-8")


def fazer_handshake(conexao, host, porta):
    """Faz o handshake inicial do WebSocket."""
    chave = base64.b64encode(os.urandom(16)).decode("ascii")
    conexao.sendall(montar_requisicao(host, porta, chave))

    resposta = conexao.recv(4096).decode("utf-8", errors="replace")
    if "101 Switching Protocols" not in resposta:
        raise ConnectionError("O servidor nao aceitou o WebSocket.")


def receber_do_servidor(conexao, parar):
    """Fica ouvindo o que o servidor mandar."""
    try:
        while not parar.is_set():
            # Cada frame que chega e mostrado na tela.
            opcode, conteudo = ler_frame_websocket(conexao)

            if opcode == 0x8:
                break

            if opcode == 0xA:
                continue

            if opcode == 0x1:
                print(conteudo.decode("utf-8", errors="replace"))
    except (ConnectionError, OSError):
        pass
    finally:
        parar.set()


def executar_cliente(host, porta, nome):
    """Conecta no servidor e deixa o usuario conversar."""
    print(cabecalho_projeto("Exercicio 10 - Cliente do Chat WebSocket"))

    parar = threading.Event()
    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conecta primeiro e depois faz o upgrade para WebSocket.
        conexao.connect((host, porta))
        fazer_handshake(conexao, host, porta)

        thread_recebimento = threading.Thread(target=receber_do_servidor, args=(conexao, parar), daemon=True)
        thread_recebimento.start()

        # A primeira mensagem enviada e o nome do participante.
        conexao.sendall(codificar_frame_websocket(nome.strip() or "Anonimo", mascarar=True))

        while not parar.is_set():
            mensagem = input()

            if mensagem.strip().lower() == "sair":
                conexao.sendall(codificar_frame_websocket("sair", mascarar=True))
                break

            if mensagem.strip() == "":
                print("A mensagem nao pode ser vazia.")
                continue

            conexao.sendall(codificar_frame_websocket(mensagem, mascarar=True))

        parar.set()
        thread_recebimento.join(timeout=2)

        try:
            enviar_fechamento_websocket(conexao)
        except OSError:
            pass
    except KeyboardInterrupt:
        parar.set()
    finally:
        fechar_socket_sem_erro(conexao)


def ler_argumentos():
    """Le os argumentos e inicia o cliente."""
    parser = argparse.ArgumentParser(description="Cliente do chat WebSocket do Exercicio 10")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--name", default="Participante")
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_cliente(args.host, args.port, args.name)

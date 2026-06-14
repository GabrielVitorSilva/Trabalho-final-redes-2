"""Exercicio 10 - Chat com WebSocket.

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
    # Adiciona a raiz do projeto para importar common.py.
    sys.path.insert(0, str(ROOT))

from common import (
    cabecalho_projeto,
    fechar_socket_sem_erro,
    codificar_frame_websocket,
    chave_aceitacao_websocket,
    ler_requisicao_http,
    ler_frame_websocket,
    enviar_fechamento_websocket,
    enviar_texto_websocket,
)


def fazer_handshake(conexao):
    """Faz o handshake basico do WebSocket."""
    primeira_linha, cabecalhos = ler_requisicao_http(conexao)

    if not primeira_linha.startswith("GET "):
        raise ValueError("Requisicao invalida.")

    upgrade = cabecalhos.get("upgrade", "").lower()
    conexao_header = cabecalhos.get("connection", "").lower()
    chave = cabecalhos.get("sec-websocket-key", "")

    if upgrade != "websocket" or "upgrade" not in conexao_header or not chave:
        raise ValueError("Cabecalhos do WebSocket ausentes.")

    resposta = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {chave_aceitacao_websocket(chave)}\r\n\r\n"
    )
    conexao.sendall(resposta.encode("utf-8"))


def enviar_para_todos(clientes, mensagem, ignorar=None):
    """Manda uma mensagem para todos, menos para quem for ignorado."""
    for cliente in clientes[:]:
        if cliente is ignorar:
            continue

        try:
            with cliente["trava"]:
                enviar_texto_websocket(cliente["conexao"], mensagem, mascarar=False)
        except OSError:
            # Se algum cliente cair, a gente so ignora.
            pass


def atender_cliente(cliente, clientes, trava_lista):
    """Fica lendo os frames de um cliente e repassa para o resto."""
    conexao = cliente["conexao"]

    try:
        # A primeira mensagem enviada pelo cliente vai ser o nome dele.
        opcode, conteudo = ler_frame_websocket(conexao)
        if opcode != 0x1:
            raise ValueError("Primeira mensagem invalida.")

        nome = conteudo.decode("utf-8", errors="replace").strip()
        if nome == "":
            nome = "Anonimo"
        cliente["nome"] = nome

        enviar_para_todos(clientes, f"Sistema: {nome} entrou no chat.", ignorar=cliente)
        with cliente["trava"]:
            enviar_texto_websocket(conexao, f"Sistema: voce entrou como {nome}.", mascarar=False)

        while True:
            # Depois do nome, cada frame de texto vira uma mensagem do chat.
            opcode, conteudo = ler_frame_websocket(conexao)

            if opcode == 0x8:
                break

            if opcode == 0x9:
                # Responde ping com pong.
                with cliente["trava"]:
                    conexao.sendall(codificar_frame_websocket(conteudo, opcode=0xA, mascarar=False))
                continue

            if opcode != 0x1:
                continue

            mensagem = conteudo.decode("utf-8", errors="replace").strip()

            if mensagem == "":
                with cliente["trava"]:
                    enviar_texto_websocket(conexao, "ERRO: mensagem vazia nao permitida.", mascarar=False)
                continue

            if mensagem.lower() == "sair":
                with cliente["trava"]:
                    enviar_texto_websocket(conexao, "Sistema: voce saiu do chat.", mascarar=False)
                break

            enviar_para_todos(clientes, f"{nome}: {mensagem}", ignorar=cliente)
    except (ConnectionError, OSError, ValueError):
        pass
    finally:
        # Tiramos o cliente da lista e avisamos os outros.
        with trava_lista:
            if cliente in clientes:
                clientes.remove(cliente)
                enviar_para_todos(clientes, f"Sistema: {cliente.get('nome', 'Anonimo')} saiu do chat.")

        try:
            with cliente["trava"]:
                enviar_fechamento_websocket(conexao)
        except OSError:
            pass

        fechar_socket_sem_erro(conexao)


def executar_servidor(host, porta):
    """Inicia o servidor WebSocket e aceita clientes."""
    print(cabecalho_projeto("Exercicio 10 - Chat com WebSocket"))

    clientes = []
    trava_lista = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Reutiliza a porta para testar o programa varias vezes.
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen()
        print(f"Servidor WebSocket ouvindo em ws://{host}:{porta}")

        try:
            while True:
                conexao, endereco = servidor.accept()

                try:
                    fazer_handshake(conexao)
                except Exception as erro:
                    print(f"Falha no handshake de {endereco[0]}:{endereco[1]}: {erro}")
                    fechar_socket_sem_erro(conexao)
                    continue

                cliente = {
                    "conexao": conexao,
                    "endereco": endereco,
                    "nome": "Anonimo",
                    "trava": threading.Lock(),
                }

                with trava_lista:
                    clientes.append(cliente)

                print(f"Cliente conectado: {endereco[0]}:{endereco[1]}")

                thread = threading.Thread(target=atender_cliente, args=(cliente, clientes, trava_lista), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\nEncerrando servidor WebSocket.")
        finally:
            with trava_lista:
                for cliente in clientes[:]:
                    try:
                        with cliente["trava"]:
                            enviar_fechamento_websocket(cliente["conexao"])
                    except OSError:
                        pass
                    fechar_socket_sem_erro(cliente["conexao"])
                clientes.clear()


def ler_argumentos():
    """Le os argumentos e inicia o servidor."""
    parser = argparse.ArgumentParser(description="Servidor do chat WebSocket do Exercicio 10")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_servidor(args.host, args.port)

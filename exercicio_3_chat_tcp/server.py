"""Exercicio 3 - Chat TCP.

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
    # Coloca a raiz do projeto no caminho para importar common.py.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, enviar_linha, fechar_socket_sem_erro


def ler_linha(conexao: socket.socket, sobra: bytes = b"") -> tuple[str | None, bytes]:
    """Le uma linha do socket e devolve o texto junto com o restante do buffer."""
    while b"\n" not in sobra:
        parte = conexao.recv(1024)
        if not parte:
            if sobra:
                return sobra.decode("utf-8", errors="replace").rstrip("\r"), b""
            return None, b""
        sobra += parte

    linha, resto = sobra.split(b"\n", 1)
    return linha.decode("utf-8", errors="replace").rstrip("\r"), resto


def ler_nome(conexao: socket.socket) -> str:
    """Le a primeira mensagem e usa isso como nome do cliente."""
    nome, _ = ler_linha(conexao)
    if not nome:
        return "Anonimo"
    return nome.strip() or "Anonimo"


def enviar_mensagem(conexao: socket.socket, trava: threading.Lock, mensagem: str) -> None:
    """Envia uma mensagem sem misturar com as outras threads."""
    try:
        with trava:
            enviar_linha(conexao, mensagem)
    except OSError:
        pass


def atender_cliente(indice: int, clientes, nomes, travas, parar: threading.Event) -> None:
    """Lendo as mensagens de um cliente e mandando para o outro."""
    conexao = clientes[indice]
    outro_indice = 1 - indice
    sobra = b""

    try:
        while not parar.is_set():
            linha, sobra = ler_linha(conexao, sobra)
            if linha is None:
                break

            mensagem = linha.strip()
            if mensagem == "":
                enviar_mensagem(conexao, travas[indice], "ERRO: mensagem vazia nao permitida.")
                continue

            if mensagem.lower() == "sair":
                enviar_mensagem(conexao, travas[indice], "Sistema: voce saiu do chat.")
                enviar_mensagem(clientes[outro_indice], travas[outro_indice], f"Sistema: {nomes[indice]} saiu do chat.")
                break

            enviar_mensagem(clientes[outro_indice], travas[outro_indice], f"{nomes[indice]}: {mensagem}")
    finally:
        parar.set()
        fechar_socket_sem_erro(conexao)


def executar_servidor(host: str, porta: int) -> None:
    """Espera dois clientes e cria o chat entre eles."""
    print(cabecalho_projeto("Exercicio 3 - Chat TCP"))

    clientes = []
    nomes = []
    travas = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(2)
        print(f"Servidor de chat ouvindo em {host}:{porta}")

        while len(clientes) < 2:
            conexao, endereco = servidor.accept()
            nome = ler_nome(conexao)

            clientes.append(conexao)
            nomes.append(nome)
            travas.append(threading.Lock())

            print(f"Cliente conectado: {nome} ({endereco[0]}:{endereco[1]})")
            enviar_mensagem(conexao, travas[-1], "Sistema: voce entrou no chat.")

        enviar_mensagem(clientes[0], travas[0], f"Sistema: chat iniciado com {nomes[1]}.")
        enviar_mensagem(clientes[1], travas[1], f"Sistema: chat iniciado com {nomes[0]}.")
        print("Dois clientes conectados. O chat ja pode ser usado.")

        parar = threading.Event()
        thread_1 = threading.Thread(target=atender_cliente, args=(0, clientes, nomes, travas, parar), daemon=True)
        thread_2 = threading.Thread(target=atender_cliente, args=(1, clientes, nomes, travas, parar), daemon=True)

        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()

        for conexao in clientes:
            fechar_socket_sem_erro(conexao)


def ler_argumentos():
    """Le os argumentos e executa o servidor."""
    parser = argparse.ArgumentParser(description="Servidor do chat TCP do Exercicio 3")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6500)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    try:
        executar_servidor(args.host, args.port)
    except KeyboardInterrupt:
        print("\nEncerrando servidor de chat.")

"""Exercicio 2 - Cliente UDP Echo.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Garante acesso ao módulo comum com o limite de payload UDP.
    sys.path.insert(0, str(ROOT))

from common import LIMITE_UDP, cabecalho_projeto


def enviar_mensagem(conexao: socket.socket, endereco_servidor: tuple[str, int], mensagem: str) -> None:
    """Envia uma mensagem validada e mostra o eco recebido."""
    texto = mensagem.strip()
    if not texto:
        # Mensagem vazia não faz sentido nesse exercício.
        print("A mensagem nao pode ser vazia.")
        return
    if texto.lower() == "sair":
        # O comando sair é tratado como encerramento voluntário do cliente.
        raise SystemExit

    pacote = texto.encode("utf-8")
    if len(pacote) > LIMITE_UDP:
        # Evita tentar enviar um datagrama acima do limite do protocolo.
        print(f"Mensagem muito grande para UDP: {len(pacote)} bytes.")
        return

    # Envia o datagrama para o servidor de eco.
    conexao.sendto(pacote, endereco_servidor)

    try:
        # Aguarda o eco dentro do timeout configurado no socket.
        dados, _ = conexao.recvfrom(65535)
    except socket.timeout:
        # Se nada voltar, informamos o timeout ao usuário.
        print("Tempo limite expirado aguardando o eco do servidor.")
        return

    print(f"Eco recebido: {dados.decode('utf-8', errors='replace')}")


def executar_cliente(host: str, port: int, mensagem: str | None, timeout: float) -> None:
    """Roda o cliente UDP em modo interativo ou de teste."""
    print(cabecalho_projeto("Exercicio 2 - Cliente UDP Echo"))
    endereco_servidor = (host, port)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        # Define timeout para não travar indefinidamente em caso de perda.
        client.settimeout(timeout)

        if mensagem is not None:
            # Modo não interativo, útil para testes automatizados.
            enviar_mensagem(client, endereco_servidor, mensagem)
            return

        while True:
            # No modo interativo, o usuário pode mandar várias mensagens.
            text = input("Mensagem (digite 'sair' para encerrar): ")
            if text.strip().lower() == "sair":
                break
            enviar_mensagem(client, endereco_servidor, text)


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Cliente UDP Echo do Exercicio 2")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--message", default=None)
    parser.add_argument("--timeout", type=float, default=3.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_cliente(args.host, args.port, args.message, args.timeout)

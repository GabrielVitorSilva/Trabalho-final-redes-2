"""Exercicio 2 - Servidor Echo UDP.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Torna possível importar o cabeçalho padrão do projeto.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto


def executar_servidor(host: str, port: int) -> None:
    """Espera datagramas UDP e devolve a mesma mensagem."""
    print(cabecalho_projeto("Exercicio 2 - Echo UDP"))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        # UDP não usa listen; basta associar a porta com bind.
        server.bind((host, port))
        print(f"Servidor UDP ouvindo em {host}:{port}")

        try:
            while True:
                # Cada datagrama recebido é devolvido exatamente como chegou.
                data, addr = server.recvfrom(65535)
                message = data.decode("utf-8", errors="replace")
                print(f"[{addr[0]}:{addr[1]}] {message}")
                server.sendto(data, addr)
        except KeyboardInterrupt:
            # Ctrl+C encerra o loop de forma limpa.
            print("\nEncerrando servidor UDP.")


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Servidor UDP Echo do Exercicio 2")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6000)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_servidor(args.host, args.port)

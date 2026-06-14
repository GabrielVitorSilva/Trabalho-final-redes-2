"""Exercicio 1 - Cliente TCP.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Permite importar os utilitários compartilhados do projeto.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, fechar_socket_sem_erro, enviar_linha


def escolher_mensagem(mensagem_explicita: str | None) -> str:
    """Pega a mensagem do argumento ou do teclado e valida."""
    if mensagem_explicita is not None:
        # Quando a mensagem vem por argumento, removemos espaços laterais.
        mensagem = mensagem_explicita.strip()
    else:
        # Sem argumento, a mensagem é coletada no terminal.
        mensagem = input("Mensagem para o servidor: ").strip()

    while not mensagem:
        # Repetimos a pergunta até o usuário informar algo válido.
        print("A mensagem nao pode ser vazia.")
        mensagem = input("Mensagem para o servidor: ").strip()

    return mensagem


def executar_cliente(host: str, port: int, mensagem: str | None) -> None:
    """Conecta no servidor TCP, envia uma mensagem e mostra a resposta."""
    print(cabecalho_projeto("Exercicio 1 - Cliente TCP"))
    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Conecta ao servidor antes de iniciar a troca de mensagens.
        conexao.connect((host, port))
        texto = escolher_mensagem(mensagem)
        enviar_linha(conexao, texto)

        # Recebe a confirmação enviada pelo servidor.
        leitor = conexao.makefile("r", encoding="utf-8", newline="\n")
        try:
            resposta = leitor.readline().rstrip("\r\n")
        finally:
            leitor.close()

        if resposta:
            print(f"Resposta do servidor: {resposta}")
        else:
            # Se o servidor encerrar antes de responder, avisamos o usuário.
            print("O servidor encerrou a conexao sem resposta.")
    finally:
        # Garante liberação do socket mesmo em caso de erro.
        fechar_socket_sem_erro(conexao)


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Cliente TCP do Exercicio 1")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--message", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_cliente(args.host, args.port, args.message)

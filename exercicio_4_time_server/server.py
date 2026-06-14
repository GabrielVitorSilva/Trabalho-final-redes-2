"""Exercicio 4 - Servidor de hora com threads.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Inclui a raiz do projeto no path para importar os utilitários.
    sys.path.insert(0, str(ROOT))

from common import cabecalho_projeto, fechar_socket_sem_erro, hora_atual, enviar_linha

LOG_PATH = Path(__file__).with_name("server.log")


def configurar_logger() -> logging.Logger:
    """Configura o logger do servidor."""
    # Centraliza logs do servidor em arquivo e também na saída padrão.
    logger = logging.getLogger("exercicio_4_time_server")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        # Mesmo formato de log nas duas saídas.
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        # Registra as requisições no arquivo server.log.
        file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Repete os logs no terminal para facilitar a depuração.
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


def atender_cliente(conexao: socket.socket, endereco: tuple[str, int], logger: logging.Logger) -> None:
    """Atende um cliente e devolve a hora atual quando pedirem."""
    with conexao:
        # Cada cliente usa um leitor de linhas próprio.
        leitor = conexao.makefile("r", encoding="utf-8", newline="\n")
        try:
            while True:
                # Aguarda a próxima solicitação do cliente.
                linha = leitor.readline()
                if linha == "":
                    # Se a leitura vier vazia, o cliente encerrou a conexão.
                    logger.info("Cliente %s:%s desconectou.", endereco[0], endereco[1])
                    break

                pedido = linha.rstrip("\r\n")
                if not pedido.strip():
                    # Solicitações em branco retornam erro explícito.
                    enviar_linha(conexao, "ERRO: solicitacao vazia nao permitida.")
                    continue

                # Gera a hora atual e registra o atendimento no log.
                agora = hora_atual()
                logger.info("Solicitacao de %s:%s | pedido=%r | resposta=%s", endereco[0], endereco[1], pedido, agora)
                enviar_linha(conexao, agora)
        finally:
            # Fecha o arquivo de leitura associado ao socket.
            leitor.close()


def executar_servidor(host: str, port: int) -> None:
    """Inicia o servidor de hora com threads."""
    logger = configurar_logger()
    print(cabecalho_projeto("Exercicio 4 - Servidor de Hora com Threads"))
    logger.info("Servidor iniciado em %s:%s", host, port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Permite reiniciar o servidor sem esperar o timeout da porta.
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, port))
        servidor.listen()
        print(f"Servidor de hora ouvindo em {host}:{port}")

        try:
            while True:
                # Cada cliente recebe uma thread própria para não bloquear o restante.
                conexao, endereco = servidor.accept()
                logger.info("Cliente conectado: %s:%s", endereco[0], endereco[1])
                thread = threading.Thread(target=atender_cliente, args=(conexao, endereco, logger), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            # O encerramento manual também é registrado no log.
            logger.info("Encerramento solicitado pelo usuario.")
            print("\nEncerrando servidor de hora.")


def ler_argumentos() -> argparse.Namespace:
    """Le os argumentos passados na linha de comando."""
    parser = argparse.ArgumentParser(description="Servidor de hora com threads do Exercicio 4")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7000)
    return parser.parse_args()


if __name__ == "__main__":
    args = ler_argumentos()
    executar_servidor(args.host, args.port)

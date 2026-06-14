"""Funcoes auxiliares compartilhadas entre os exercicios de rede.

Participantes: Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra
"""

from __future__ import annotations

import base64
import hashlib
import os
import socket
import struct
from datetime import datetime

INTEGRANTES = "Gabriel Vitor, Pedro Augusto Hackner, Ana Clara Azevedo, Joao Pedro Marra"
LIMITE_UDP = 65507


def cabecalho_projeto(titulo: str) -> str:
    """Monta um cabecalho simples para o terminal."""
    return f"{titulo}\nParticipantes: {INTEGRANTES}"


def enviar_linha(conexao: socket.socket, texto: str) -> None:
    """Envia uma linha de texto UTF-8 pelo socket."""
    pacote = (texto.rstrip("\r\n") + "\n").encode("utf-8")
    conexao.sendall(pacote)


def ler_exato(conexao: socket.socket, tamanho: int) -> bytes:
    """Le exatamente a quantidade de bytes pedida."""
    dados = bytearray()
    while len(dados) < tamanho:
        parte = conexao.recv(tamanho - len(dados))
        if not parte:
            raise ConnectionError("Conexao encerrada durante a leitura")
        dados.extend(parte)
    return bytes(dados)


def ler_ate(conexao: socket.socket, marcador: bytes = b"\r\n\r\n", limite: int = 65536) -> bytes:
    """Le bytes ate encontrar um marcador."""
    dados = bytearray()
    while marcador not in dados:
        parte = conexao.recv(4096)
        if not parte:
            break
        dados.extend(parte)
        if len(dados) > limite:
            raise ValueError("Cabecalho HTTP excedeu o limite permitido")
    return bytes(dados)


def separar_cabecalhos_http(requisicao_bruta: bytes) -> tuple[str, dict[str, str]]:
    """Separa a linha inicial e os cabecalhos de uma requisicao HTTP."""
    texto = requisicao_bruta.decode("utf-8", errors="replace")
    linhas = texto.split("\r\n")
    primeira_linha = linhas[0] if linhas else ""
    cabecalhos: dict[str, str] = {}

    for linha in linhas[1:]:
        if not linha:
            continue
        chave, separador, valor = linha.partition(":")
        if separador:
            cabecalhos[chave.strip().lower()] = valor.strip()

    return primeira_linha, cabecalhos


def chave_aceitacao_websocket(chave_cliente: str) -> str:
    """Cria o valor Sec-WebSocket-Accept do handshake."""
    segredo = chave_cliente.strip() + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    digest = hashlib.sha1(segredo.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def codificar_frame_websocket(dados: str | bytes, *, opcode: int = 0x1, mascarar: bool = False) -> bytes:
    """Monta um frame WebSocket."""
    payload = dados.encode("utf-8") if isinstance(dados, str) else dados
    byte_inicial = 0x80 | (opcode & 0x0F)
    mascara = 0x80 if mascarar else 0
    tamanho = len(payload)
    cabecalho = bytearray([byte_inicial])

    if tamanho < 126:
        cabecalho.append(mascara | tamanho)
    elif tamanho <= 0xFFFF:
        cabecalho.append(mascara | 126)
        cabecalho.extend(struct.pack("!H", tamanho))
    else:
        cabecalho.append(mascara | 127)
        cabecalho.extend(struct.pack("!Q", tamanho))

    if not mascarar:
        return bytes(cabecalho) + payload

    chave_mascara = os.urandom(4)
    mascarado = bytes(byte ^ chave_mascara[i % 4] for i, byte in enumerate(payload))
    return bytes(cabecalho) + chave_mascara + mascarado


def enviar_texto_websocket(conexao: socket.socket, texto: str, *, mascarar: bool = False) -> None:
    """Envia um frame WebSocket de texto."""
    conexao.sendall(codificar_frame_websocket(texto, opcode=0x1, mascarar=mascarar))


def enviar_fechamento_websocket(conexao: socket.socket, *, codigo: int = 1000, motivo: str = "") -> None:
    """Envia um frame de fechamento do WebSocket."""
    payload = struct.pack("!H", codigo) + motivo.encode("utf-8")
    conexao.sendall(codificar_frame_websocket(payload, opcode=0x8, mascarar=False))


def ler_frame_websocket(conexao: socket.socket) -> tuple[int, bytes]:
    """Le um frame WebSocket e retorna opcode e conteudo."""
    dois_primeiros = ler_exato(conexao, 2)
    primeiro_byte, segundo_byte = dois_primeiros[0], dois_primeiros[1]
    opcode = primeiro_byte & 0x0F
    mascarado = bool(segundo_byte & 0x80)
    tamanho = segundo_byte & 0x7F

    if tamanho == 126:
        tamanho = struct.unpack("!H", ler_exato(conexao, 2))[0]
    elif tamanho == 127:
        tamanho = struct.unpack("!Q", ler_exato(conexao, 8))[0]

    chave_mascara = ler_exato(conexao, 4) if mascarado else b""
    payload = ler_exato(conexao, tamanho) if tamanho else b""

    if mascarado:
        payload = bytes(byte ^ chave_mascara[i % 4] for i, byte in enumerate(payload))

    return opcode, payload


def ler_requisicao_http(conexao: socket.socket) -> tuple[str, dict[str, str]]:
    """Le uma requisicao HTTP simples usada no handshake."""
    return separar_cabecalhos_http(ler_ate(conexao))


def hora_atual() -> str:
    """Retorna a hora atual no formato HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


def fechar_socket_sem_erro(conexao: socket.socket | None) -> None:
    """Fecha um socket sem mostrar erro se ele ja estiver fechado."""
    if conexao is None:
        return
    try:
        conexao.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    finally:
        try:
            conexao.close()
        except OSError:
            pass

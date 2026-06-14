# Trabalho 2 de Redes de Computadores 2

## Integrantes

- Gabriel Vitor
- Pedro Augusto Hackner
- Ana Clara Azevedo
- Joao Pedro Marra

## Estrutura

Os codigos foram separados por exercicio, para ficar mais facil de achar cada parte.

- `common.py`
- `exercicio_1_tcp/`
- `exercicio_2_udp_echo/`
- `exercicio_3_chat_tcp/`
- `exercicio_4_time_server/`
- `exercicio_10_websocket_chat/`

Os exercicios 5 a 9 sao de captura e analise no Wireshark, entao nao precisam de codigo em Python.

## Como executar

Use Python 3.10 ou superior.

### Exercicio 1 - TCP cliente/servidor

```bash
python3 exercicio_1_tcp/server.py --host 0.0.0.0 --port 5000
python3 exercicio_1_tcp/client.py --host 127.0.0.1 --port 5000
```

### Exercicio 2 - Echo UDP

```bash
python3 exercicio_2_udp_echo/server.py --host 0.0.0.0 --port 6000
python3 exercicio_2_udp_echo/client.py --host 127.0.0.1 --port 6000
```

### Exercicio 3 - Chat TCP

Abra o servidor e depois rode dois clientes, um em cada terminal.

```bash
python3 exercicio_3_chat_tcp/server.py --host 0.0.0.0 --port 6500
python3 exercicio_3_chat_tcp/client.py --host 127.0.0.1 --port 6500 --name Alice
python3 exercicio_3_chat_tcp/client.py --host 127.0.0.1 --port 6500 --name Bob
```

### Exercicio 4 - Servidor de hora com threads

```bash
python3 exercicio_4_time_server/server.py --host 0.0.0.0 --port 7000
python3 exercicio_4_time_server/client.py --host 127.0.0.1 --port 7000
```

### Exercicio 10 - Chat com WebSockets

```bash
python3 exercicio_10_websocket_chat/server.py --host 0.0.0.0 --port 8765
python3 exercicio_10_websocket_chat/client.py --host 127.0.0.1 --port 8765 --name Alice
python3 exercicio_10_websocket_chat/client.py --host 127.0.0.1 --port 8765 --name Bob
```

## Observacoes

- Todos os scripts tem comentarios e o nome dos participantes.
- O exercicio 4 gera um arquivo `server.log` dentro da pasta dele.
- O chat do exercicio 10 usa apenas a biblioteca padrao do Python.

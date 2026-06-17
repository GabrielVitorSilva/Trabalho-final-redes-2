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

## Como rodar em dois computadores na mesma rede

Se o servidor estiver em um computador e o cliente em outro, siga esta regra:

- No computador do servidor, use `--host 0.0.0.0`
- No computador do cliente, use o IP real do computador do servidor na rede local

Exemplo:

```bash
python3 exercicio_1_tcp/server.py --host 0.0.0.0 --port 5000
python3 exercicio_1_tcp/client.py --host 192.168.0.10 --port 5000
```

`192.168.0.10` e apenas um exemplo. O IP certo pode ser visto com `ipconfig` no Windows, `ip a` no Linux ou `ipconfig getifaddr en0` no macOS.

### Como descobrir o IP do computador

- No Windows, abra o Prompt de Comando e rode:
  ```bash
  ipconfig
  ```
- No Linux, abra o terminal e rode:
  ```bash
  ip a
  ```
- No macOS, abra o terminal e rode:
  ```bash
  ipconfig getifaddr en0
  ```

Procure o endereco da interface de rede usada na sua conexao, como Wi-Fi ou cabo. Normalmente ele aparece como algo parecido com `192.168.x.x` ou `10.x.x.x`.

Se a porta estiver ocupada, troque para outra porta livre, como `5001`, `6001`, `6501`, `7001` ou `8766`.

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
- Para teste entre computadores, sempre deixe o servidor escutando em `0.0.0.0` e o cliente apontando para o IP local do servidor.

""" import json
import time
import psycopg2
from kafka import KafkaProducer
from psycopg2.extras import RealDictCursor

Pequeno teste inicial para certificar se os containers estão funcionando. Consiste em uma integração entre um banco de dados gerado a partir de uma imagem do Postgres por meio do Docker e o Kafka como sistema de mensageria para uma monitoração em tempo real da retirada ou recebimento de medicamentos de um estoque ficticio. Producer(Extrator dos dados do DB) -> Kafka (garantindo que a mensagem chegue) -> Consumer(Monitor em tempo real), atuando como um painel de monitoramento que lê as mensagens do tópico e exibe as entradas e saídas instantaneamente no terminal.

producer = KafkaProducer(
    bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
    client_id='extrator-oltp',
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8') # default=str converte as datas do Postgres
)

# Conexão com o Banco OLTP
def pegar_Conexao_Db():
    return psycopg2.connect(
        host = "localhost",
        database = "farmacia_db",
        user = "admin",
        password = "adminpassword",
        port = "5433"
    )

print("Iniciando o extrator OLTP -> Kafka...")


try:
    while True:
        conn = pegar_Conexao_Db()

        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM movimentacao_estoque WHERE processado = FALSE ORDER BY id ASC;")
        novos_registros = cur.fetchall()

        if novos_registros:
            print(f"Encontrados {len(novos_registros)} novos registros encontrados no banco. Enviando para o Kafka...")

            ids_processados = []
            for linha in novos_registros:
                # O payload do evento exato como sai do banco
                evento = dict(linha)
                #envia para o topico do kafka
                producer.send('teste', value=evento)
                ids_processados.append(linha['id'])

                print(f"  -> Enviado: {evento['medicamento']} | Qtd: {evento['quantidade']}")
                time.sleep(0.5) # Pausa apenas para visualização no teste

            producer.flush()

            if ids_processados:
                cur.execute(
                    "UPDATE movimentacao_estoque SET processado = TRUE WHERE id = ANY(%s)",(ids_processados,)
                )
                conn.commit()
                print(" Banco atualizado (Registros marcados como processados).\n")
            else:
                print(" Nenhum dado novo no banco. Aguardando...")

            cur.close()
            conn.close()
            
            time.sleep(5) #vai esperar 5 segundos antes de checar o banco novamente

except KeyboardInterrupt:
    print("\n Extrator desligado.")"""

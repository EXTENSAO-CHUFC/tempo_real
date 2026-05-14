import json
import redis
from kafka import KafkaConsumer

def run_redis_consumer():
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    consumer = KafkaConsumer(
        'teste',
        bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print(" Consumidor Redis iniciado!")
    print("Ouvindo mensagens do Kafka para atualizar o cache em tempo real...\n")

    try:
        for mensagem in consumer:
            evento = mensagem.value
            id_med = evento['id_medicamento']
            qtd_retirada = evento['quantidade']
            
            novo_saldo = redis_client.decrby(f"estoque:{id_med}", qtd_retirada)
            
            if novo_saldo < 0:
                redis_client.set(f"estoque:{id_med}", 0)
                novo_saldo = 0
                
            print(f" [REDIS] Medicamento {id_med} atualizado para: {novo_saldo} unidades")
            
    except KeyboardInterrupt:
        print("\n Encerrando o Consumidor Redis.")
        
    finally:
        consumer.close()
        print("Conexão com o Kafka encerrada.")

if __name__ == "__main__":
    run_redis_consumer()
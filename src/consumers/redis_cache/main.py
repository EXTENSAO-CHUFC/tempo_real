from src.utils.kafka import get_kafka_consumer
from src.utils.redis_client import get_redis_client
from src.config.settings import settings

def run_redis_consumer():
    # Instanciamento limpo usando Utils
    redis_client = get_redis_client()
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id=None)

    print("Consumidor Redis iniciado!")
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
                
            print(f"⚡ [REDIS] Medicamento {id_med} atualizado para: {novo_saldo} unidades")
            
    except KeyboardInterrupt:
        print("\n Encerrando o Consumidor Redis...")
    finally:
        consumer.close()
        print("Conexão com o Kafka encerrada.")

if __name__ == "__main__":
    run_redis_consumer()
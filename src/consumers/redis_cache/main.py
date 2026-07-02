import json
from datetime import datetime
from src.utils.kafka import get_kafka_consumer
from src.utils.redis_client import get_redis_client
from src.config.settings import settings

def run_redis_consumer():
    redis_client = get_redis_client()
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id=None)

    print("Consumidor Redis iniciado!")
    print("Ouvindo mensagens do Kafka para atualizar o saldo por lote em tempo real...\n")

    try:
        for mensagem in consumer:
            evento = mensagem.value
            lote_id = evento['lote_id']
            tipo = evento['tipo_movimento']
            quantidade = evento['quantidade']
            medicamento = evento.get('medicamento', f'Lote {lote_id}')

            # ENTRADA soma, SAIDA subtrai — saldo é sempre calculado, nunca um valor fixo
            if tipo == "ENTRADA":
                novo_saldo = redis_client.incrby(f"saldo_lote:{lote_id}", quantidade)
            else:
                novo_saldo = redis_client.decrby(f"saldo_lote:{lote_id}", quantidade)

            # saldo não pode ser negativo — se for, corrige para 0.
            if novo_saldo < 0:
                redis_client.set(f"saldo_lote:{lote_id}", 0)
                novo_saldo = 0

            print(f"⚡ [REDIS] Lote {lote_id} ({medicamento}) atualizado para: {novo_saldo} unidades")

            hora_agora = datetime.now().strftime("%H:%M:%S")
            registro_feed = {
                "Horário": hora_agora,
                "Lote": lote_id,
                "Tipo": tipo,
                "Quantidade": quantidade,
                "Medicamento": medicamento
            }

            redis_client.lpush("feed_movimentacoes", json.dumps(registro_feed))
            redis_client.ltrim("feed_movimentacoes", 0, 14)

    except KeyboardInterrupt:
        print("\n Encerrando o Consumidor Redis...")
    finally:
        consumer.close()
        print("Conexão com o Kafka encerrada.")

if __name__ == "__main__":
    run_redis_consumer()
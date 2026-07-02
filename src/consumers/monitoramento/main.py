from src.utils.kafka import get_kafka_consumer
from src.utils.redis_client import get_redis_client
from src.config.settings import settings
from src.consumers.monitoramento.handler import avaliar_estoque, limpar_alerta


def run_monitoramento_consumer():
    redis_client = get_redis_client()
    # group_id próprio: este consumer lê o MESMO tópico que os outros,
    # de forma independente — Kafka entrega a mesma mensagem para
    # cada group_id diferente, sem interferir no redis_cache ou no historico.
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id='grupo_monitoramento')

    print("Consumidor de Monitoramento iniciado!")
    print("Verificando se alguma movimentação zera o saldo de um lote...\n")

    try:
        for mensagem in consumer:
            evento = mensagem.value
            lote_id = evento['lote_id']
            medicamento = evento.get('medicamento', f'Lote {lote_id}')
            tipo = evento['tipo_movimento']

           
            saldo_redis = redis_client.get(f"saldo_lote:{lote_id}")
            saldo_atual = int(saldo_redis) if saldo_redis is not None else None

            if saldo_atual is None:
                print(f"[MONITORAMENTO] Saldo do lote {lote_id} ainda não está no cache. Ignorando.")
                continue

            if tipo == "ENTRADA" and saldo_atual > 0:
                # Reabasteceu: se havia alerta ativo para esse lote, encerra.
                limpar_alerta(lote_id, redis_client)

            avaliar_estoque(saldo_atual, lote_id, medicamento, redis_client)

    except KeyboardInterrupt:
        print("\nEncerrando o Consumidor de Monitoramento...")
    finally:
        consumer.close()
        print("Conexão do Consumidor de Monitoramento (Kafka) encerrada.")


if __name__ == "__main__":
    run_monitoramento_consumer()
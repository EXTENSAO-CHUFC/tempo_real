import random
import threading

from src.utils.kafka import get_kafka_consumer, get_kafka_producer
from src.utils.redis_client import get_redis_client
from src.utils.db import get_db_session
from src.config.settings import settings
from src.producer.extract import simular_reabastecimento
from src.producer.transform import preparar_mensagem_kafka

DELAY_MIN_SEGUNDOS = 30
DELAY_MAX_SEGUNDOS = 60


def _processar_reabastecimento(lote_id: int, medicamento: str, producer):
    """
    Executado após o delay simulado de entrega do fornecedor. Simula a entrada real do lote no estoque
    """
    db = get_db_session()
    try:
        evento_entrada = simular_reabastecimento(db, lote_id)
        if not evento_entrada:
            print(f"[SCHEDULER] Lote {lote_id} ({medicamento}) já está no estoque_maximo, "
                  f"nada a repor.")
            return

        entrada_pronta = preparar_mensagem_kafka(evento_entrada)
        producer.send(settings.KAFKA_TOPIC_MOVIMENTACAO, value=entrada_pronta)
        producer.flush()
        print(f"[SCHEDULER] Reabastecimento entregue: +{entrada_pronta['quantidade']} "
              f"unidades de {entrada_pronta['medicamento']} (lote {entrada_pronta['lote_id']})")
    finally:
        db.close()


def run_scheduler():
    """
    Processo independente do producer de saídas e do consumer de monitoramento. Fica escutando o tópico de reabastecimento
    """
    redis_client = get_redis_client()
    producer = get_kafka_producer()
    consumer = get_kafka_consumer(
        topic=settings.KAFKA_TOPIC_REABASTECIMENTO,
        group_id='grupo_scheduler_reabastecimento',
    )

    print("Scheduler de Reabastecimento iniciado!")
    print(f"Aguardando pedidos no tópico '{settings.KAFKA_TOPIC_REABASTECIMENTO}'...\n")

    try:
        for mensagem in consumer:
            pedido = mensagem.value
            lote_id = pedido['lote_id']
            medicamento = pedido.get('medicamento', f'Lote {lote_id}')

            delay = random.randint(DELAY_MIN_SEGUNDOS, DELAY_MAX_SEGUNDOS)
            print(f"[SCHEDULER] Pedido recebido para o lote {lote_id} ({medicamento}). "
                  f"Reabastecimento chega em {delay}s...")

            timer = threading.Timer(
                delay,
                _processar_reabastecimento,
                args=(lote_id, medicamento, producer),
            )
            timer.daemon = True
            timer.start()

    except KeyboardInterrupt:
        print("\nEncerrando o Scheduler de Reabastecimento...")
    finally:
        consumer.close()
        producer.close()
        print("Conexão do Scheduler (Kafka) encerrada.")


if __name__ == "__main__":
    run_scheduler()
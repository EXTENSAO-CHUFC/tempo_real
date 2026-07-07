import threading
import time

from src.utils.kafka import get_kafka_consumer, get_kafka_producer
from src.utils.redis_client import get_redis_client
from src.config.settings import settings
from src.consumers.monitoramento.handler import avaliar_estoque, limpar_alerta

INTERVALO_VARREDURA_SEGUNDOS = 15


def _buscar_meta_lote(redis_client, lote_id, medicamento_fallback=None):
    """
     lê estoque_maximo e bloqueio_reabastecimento do cache Redis
    """
    meta = redis_client.hgetall(f"meta_lote:{lote_id}")
    if not meta:
        return None

    return {
        "estoque_maximo": int(meta["estoque_maximo"]),
        "bloqueio_reabastecimento": bool(int(meta["bloqueio_reabastecimento"])),
        "medicamento": meta.get("medicamento", medicamento_fallback),
    }


def _avaliar_lote(redis_client, kafka_producer, lote_id, medicamento_fallback=None):
    """
    Reavalia um lote específico direto a partir do estado atual no Redis,
    sem depender de nenhuma mensagem Kafka ter chegado.
    """
    saldo_redis = redis_client.get(f"saldo_lote:{lote_id}")
    if saldo_redis is None:
        return

    meta = _buscar_meta_lote(redis_client, lote_id, medicamento_fallback)
    if meta is None:
        return

    saldo_atual = int(saldo_redis)

    if saldo_atual > meta["estoque_maximo"] * 0.10:
        limpar_alerta(lote_id, redis_client)

    avaliar_estoque(
        saldo=saldo_atual,
        lote_id=lote_id,
        medicamento=meta["medicamento"],
        estoque_maximo=meta["estoque_maximo"],
        bloqueio_reabastecimento=meta["bloqueio_reabastecimento"],
        redis_client=redis_client,
        kafka_producer=kafka_producer,
        topico_reabastecimento=settings.KAFKA_TOPIC_REABASTECIMENTO,
    )


def _loop_varredura_periodica(redis_client, kafka_producer):
    """
    Roda em thread separada. A cada INTERVALO_VARREDURA_SEGUNDOS, passa por
    todos os lotes conhecidos no Redis e reavalia o critério de estoque mínimo (10%).
    """
    while True:
        time.sleep(INTERVALO_VARREDURA_SEGUNDOS)
        try:
            for chave in redis_client.scan_iter(match="meta_lote:*"):
                lote_id = chave.split(":")[-1]
                _avaliar_lote(redis_client, kafka_producer, lote_id)
        except Exception as e:
            print(f"[MONITORAMENTO][VARREDURA] Erro durante varredura periódica: {e}")


def run_monitoramento_consumer():
    redis_client = get_redis_client()
    kafka_producer = get_kafka_producer()
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id='grupo_monitoramento')

    print("Consumidor de Monitoramento iniciado!")
    print("Verificando o critério de estoque mínimo (10%) a cada movimentação "
          f"e a cada {INTERVALO_VARREDURA_SEGUNDOS}s via varredura periódica...\n")

    varredura = threading.Thread(
        target=_loop_varredura_periodica,
        args=(redis_client, kafka_producer),
        daemon=True,
    )
    varredura.start()

    try:
        for mensagem in consumer:
            evento = mensagem.value
            lote_id = evento['lote_id']
            medicamento = evento.get('medicamento', f'Lote {lote_id}')

            _avaliar_lote(redis_client, kafka_producer, lote_id, medicamento)

    except KeyboardInterrupt:
        print("\nEncerrando o Consumidor de Monitoramento...")
    finally:
        consumer.close()
        kafka_producer.close()
        print("Conexão do Consumidor de Monitoramento (Kafka) encerrada.")


if __name__ == "__main__":
    run_monitoramento_consumer()
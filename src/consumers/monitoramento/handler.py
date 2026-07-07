from datetime import datetime
import json

LIMIAR_PERCENTUAL = 0.10  


def avaliar_estoque(saldo: int, lote_id: int, medicamento: str, estoque_maximo: int,
                     bloqueio_reabastecimento: bool, redis_client, kafka_producer,
                     topico_reabastecimento: str):
    """
    Critério de estoque mínimo (10%): dispara alerta sempre que o saldo cair
    igual ou abaixo de 10% do estoque_maximo do lote — não só quando zera.
    """
    limiar = estoque_maximo * LIMIAR_PERCENTUAL

    if saldo > limiar:
        return False

    alerta = {
        "lote_id": lote_id,
        "medicamento": medicamento,
        "saldo": saldo,
        "estoque_maximo": estoque_maximo,
        "limiar": limiar,
        "bloqueio_reabastecimento": bloqueio_reabastecimento,
        "hora": datetime.now().strftime("%H:%M:%S"),
        "data_hora": datetime.now().isoformat(),
    }

    redis_client.lpush("alertas_criticos", json.dumps(alerta))
    redis_client.ltrim("alertas_criticos", 0, 14)

    # Flag rápida por lote, útil para consultas pontuais ("esse lote está crítico?")
    redis_client.set(f"alerta:lote:{lote_id}", "1")

    print(f"🚨 [ALERTA] Lote {lote_id} de {medicamento} chegou a {saldo}/{estoque_maximo} "
          f"unidades (≤ {limiar:.0f}, limiar de 10%)!")

    if bloqueio_reabastecimento:
        print(f"⛔ [BLOQUEIO] {medicamento} (lote {lote_id}) está marcado para NÃO ser "
              f"reabastecido automaticamente. Alerta permanece ativo.")
        return True

    
    ja_pendente = redis_client.get(f"reabastecimento_pendente:lote:{lote_id}")
    if ja_pendente:
        return True

    redis_client.set(f"reabastecimento_pendente:lote:{lote_id}", "1", ex=180)

    pedido = {
        "lote_id": lote_id,
        "medicamento": medicamento,
        "saldo": saldo,
        "estoque_maximo": estoque_maximo,
        "solicitado_em": datetime.now().isoformat(),
    }
    kafka_producer.send(topico_reabastecimento, value=pedido)
    kafka_producer.flush()
    print(f"📨 [REABASTECIMENTO] Pedido publicado para o lote {lote_id} de {medicamento}.")

    return True


def limpar_alerta(lote_id: int, redis_client):
    """
    Remove a flag de alerta e a flag de pedido pendente quando uma entrada
    repõe o saldo de um lote que estava em estado crítico.
    """
    redis_client.delete(f"alerta:lote:{lote_id}")
    redis_client.delete(f"reabastecimento_pendente:lote:{lote_id}")
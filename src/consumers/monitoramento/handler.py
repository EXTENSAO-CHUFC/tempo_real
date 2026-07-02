from datetime import datetime
import json


def avaliar_estoque(novo_saldo: int, lote_id: int, medicamento: str, redis_client):
   
    if novo_saldo > 0:
        return False

    alerta = {
        "lote_id": lote_id,
        "medicamento": medicamento,
        "saldo": novo_saldo,
        "hora": datetime.now().strftime("%H:%M:%S"),
        "data_hora": datetime.now().isoformat(),
    }

    redis_client.lpush("alertas_criticos", json.dumps(alerta))
    redis_client.ltrim("alertas_criticos", 0, 14)

    # Flag rápida por lote, útil para consultas pontuais ("esse lote zerou?")
    redis_client.set(f"alerta:lote:{lote_id}", "1")

    print(f"🚨 [ALERTA] Lote {lote_id} de {medicamento} chegou a {novo_saldo} unidades!")
    return True


def limpar_alerta(lote_id: int, redis_client):
    """
    Remove a flag de alerta quando uma entrada repõe o saldo
    de um lote que estava zerado.
    """
    redis_client.delete(f"alerta:lote:{lote_id}")
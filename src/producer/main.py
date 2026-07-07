import time
from src.utils.kafka import get_kafka_producer
from src.utils.db import get_db_session
from src.producer.extract import simular_saida
from src.producer.transform import preparar_mensagem_kafka
from src.config.settings import settings

def run_producer():
    producer = get_kafka_producer()

    print("Producer (Simulador de Saídas) iniciado!")
    print("Gerando eventos de dispensação (saída) por lote a cada 15s e enviando para o Kafka...")
    print("O reabastecimento agora é um processo independente (src/jobs/scheduler.py).")
    print("Pressione Ctrl+C para parar.\n")

    try:
        while True:
            db = get_db_session()
            try:
                evento_saida = simular_saida(db)
                if evento_saida:
                    # TRANSFORM
                    saida_pronta = preparar_mensagem_kafka(evento_saida)

                    # LOAD
                    producer.send(settings.KAFKA_TOPIC_MOVIMENTACAO, value=saida_pronta)
                    producer.flush()
                    print(f"[KAFKA] Saída: -{saida_pronta['quantidade']} unidades "
                          f"de {saida_pronta['medicamento']} (lote {saida_pronta['lote_id']})")
                    print("-" * 40)
                else:
                    print("Nenhum lote com saldo disponível para saída!")

            finally:
                db.close()

           
            time.sleep(15)

    except KeyboardInterrupt:
        print("\nSimulador desligado com sucesso. 👋")
    finally:
        producer.close()
        print("Conexão do Producer com o Kafka encerrada.")

if __name__ == "__main__":
    run_producer()
from src.utils.kafka import get_kafka_consumer
from src.utils.db import get_db_session
from db.models import EstoqueMedicamento
from src.config.settings import settings

def run_postgres_consumer():
    # Instanciamento limpo usando Utils
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id='grupo_historico_postgres')
    db = get_db_session()

    print("Consumidor Histórico (PostgreSQL) iniciado!")
    print("Ouvindo mensagens do Kafka para atualizar o Banco de Dados oficial...\n")

    try:
        for mensagem in consumer:
            evento = mensagem.value
            id_med = evento['id_medicamento']
            qtd_retirada = evento['quantidade']

            medicamento = db.query(EstoqueMedicamento).filter(EstoqueMedicamento.id == id_med).first()

            if medicamento:
                medicamento.estoque_atual = max(0, medicamento.estoque_atual - qtd_retirada)
                db.commit()
                print(f"[POSTGRES] Estoque de {medicamento.medicamento} atualizado no banco para: {medicamento.estoque_atual}")
            else:
                print(f"[POSTGRES] Medicamento com ID {id_med} não foi encontrado no banco.")

    except KeyboardInterrupt:
        print("\nEncerrando o Consumidor Histórico...")
    finally:
        db.close()
        consumer.close()
        print("Conexões do Consumidor Histórico (DB e Kafka) encerradas.")

if __name__ == "__main__":
    run_postgres_consumer()
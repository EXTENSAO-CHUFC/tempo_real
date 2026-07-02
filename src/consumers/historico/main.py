from src.utils.kafka import get_kafka_consumer
from src.utils.db import get_db_session
from src.models.estoque import Lote, Movimentacao, TipoMovimentacao
from src.config.settings import settings

def run_postgres_consumer():
    # Instanciamento limpo usando Utils
    consumer = get_kafka_consumer(topic=settings.KAFKA_TOPIC_MOVIMENTACAO, group_id='grupo_historico_postgres')
    db = get_db_session()

    print("Consumidor Histórico (PostgreSQL) iniciado!")
    print("Ouvindo mensagens do Kafka para registrar movimentações no Banco de Dados oficial...\n")

    try:
        for mensagem in consumer:
            evento = mensagem.value
            lote_id = evento['lote_id']
            tipo = evento['tipo_movimento']
            quantidade = evento['quantidade']
            origem_destino = evento.get('origem_destino')

            lote = db.query(Lote).filter(Lote.id == lote_id).first()

            if lote:
                movimentacao = Movimentacao(
                    lote_id=lote_id,
                    tipo=TipoMovimentacao(tipo),
                    quantidade=quantidade,
                    origem_destino=origem_destino,
                )
                db.add(movimentacao)
                db.commit()
                print(f"[POSTGRES] Movimentação registrada: {tipo} de {quantidade} unidades no lote {lote_id}")
            else:
                print(f"[POSTGRES] Lote com ID {lote_id} não foi encontrado no banco.")

    except KeyboardInterrupt:
        print("\nEncerrando o Consumidor Histórico...")
    finally:
        db.close()
        consumer.close()
        print("Conexões do Consumidor Histórico (DB e Kafka) encerradas.")

if __name__ == "__main__":
    run_postgres_consumer()
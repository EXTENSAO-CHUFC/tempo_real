import time
from src.utils.kafka import get_kafka_producer
from src.utils.db import get_db_session
from src.producer.extract import simular_entrada, simular_saida
from src.producer.transform import preparar_mensagem_kafka
from src.config.settings import settings

def run_producer():
    # Inicialização limpa via utils
    producer = get_kafka_producer()

    print("Producer (Simulador de Entradas e Saídas) iniciado!")
    print("Gerando eventos de movimentação por lote e enviando para o Kafka...")
    print("Pressione Ctrl+C para parar.\n")

    try:
        while True:
            # Abre a sessão a cada ciclo para evitar cache e ler os dados reais do banco
            db = get_db_session()
            try:
                houve_movimentacao = False

                # 1. EXTRACT — entrada (reabastecimento de um lote)
                evento_entrada = simular_entrada(db)
                if evento_entrada:
                    # 2. TRANSFORM
                    entrada_pronta = preparar_mensagem_kafka(evento_entrada)

                    # 3. LOAD
                    producer.send(settings.KAFKA_TOPIC_MOVIMENTACAO, value=entrada_pronta)
                    print(f"[KAFKA] Entrada: +{entrada_pronta['quantidade']} unidades "
                          f"de {entrada_pronta['medicamento']} (lote {entrada_pronta['lote_id']})")
                    houve_movimentacao = True

                # 1. EXTRACT — saída (dispensação de um lote)
                evento_saida = simular_saida(db)
                if evento_saida:
                    # 2. TRANSFORM
                    saida_pronta = preparar_mensagem_kafka(evento_saida)

                    # 3. LOAD
                    producer.send(settings.KAFKA_TOPIC_MOVIMENTACAO, value=saida_pronta)
                    print(f"[KAFKA] Saída: -{saida_pronta['quantidade']} unidades "
                          f"de {saida_pronta['medicamento']} (lote {saida_pronta['lote_id']})")
                    houve_movimentacao = True

                if houve_movimentacao:
                    producer.flush()
                    print("-" * 40)
                else:
                    print("Nenhum lote com saldo disponível! Aguardando reposição...")

            finally:
                # Fecha a sessão a cada repetição
                db.close()

            time.sleep(3)

    except KeyboardInterrupt:
        print("\nSimulador desligado com sucesso. 👋")
    finally:
        producer.close()
        print("Conexão do Producer com o Kafka encerrada.")

if __name__ == "__main__":
    run_producer()
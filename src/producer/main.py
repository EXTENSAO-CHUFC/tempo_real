import time
from src.utils.kafka import get_kafka_producer
from src.utils.db import get_db_session
from src.producer.extract import simular_requisicao
from src.producer.transform import preparar_mensagem_kafka

def run_producer():
    # Inicialização limpa via utils
    producer = get_kafka_producer()

    print("Producer (Simulador de Saídas) iniciado!")
    print("Gerando eventos de movimentação de estoque e enviando para o Kafka...")
    print("Pressione Ctrl+C para parar.\n")

    try:
        while True:
            # Abre a sessão a cada ciclo para evitar cache e ler os dados reais do banco
            db = get_db_session()
            try:
                # 1. EXTRACT
                evento_bruto = simular_requisicao(db)

                if evento_bruto:
                    # 2. TRANSFORM
                    evento_pronto = preparar_mensagem_kafka(evento_bruto)

                    # 3. LOAD (Apenas Kafka, fim do dual-write)
                    producer.send('teste', value=evento_pronto)
                    producer.flush() 
                    
                    print(f"[KAFKA] Enviado: {evento_pronto['quantidade']} unidades de {evento_pronto['medicamento']}")
                    print("-" * 40)
                else:
                    print("Todos os estoques estão zerados! Aguardando reposição...")

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
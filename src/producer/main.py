import time
import json
import sys
import os
from kafka import KafkaProducer


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from db.connection import SessionLocal


from extract import simular_requisicao
from transform import preparar_mensagem_kafka
from checkpoint import atualizar_estoque_banco

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
        client_id='simulador-saidas',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Iniciando Simulador de Requisições (Producer)...")
    print("Pressione Ctrl+C para parar.\n")

    try:
        while True:
            db = SessionLocal()
            try:
                evento_bruto = simular_requisicao(db)

                if evento_bruto:
                    evento_pronto = preparar_mensagem_kafka(evento_bruto)

                    producer.send('teste', value=evento_pronto)
                    producer.flush() 
                    
                    print(f"📤 [KAFKA] Enviado: {evento_pronto['quantidade']} unidades de {evento_pronto['medicamento']}")

                    # Atualiza o Banco de Dados
                    atualizar_estoque_banco(db, evento_pronto['id_medicamento'], evento_pronto['quantidade'])
                    print(f"💾 [BANCO] Estoque atualizado!")
                    print("-" * 40)

                else:
                    print("⚠️ Todos os estoques estão zerados! Aguardando reposição...")

            finally:
                db.close() 

            
            time.sleep(3) 

    except KeyboardInterrupt:
        print("\n🛑 Simulador desligado com sucesso.")

if __name__ == "__main__":
    run_producer()
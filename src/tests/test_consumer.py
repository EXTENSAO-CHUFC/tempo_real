import json
import os
from kafka import KafkaConsumer

"""Pequeno teste inicial para certificar se os containers estão funcionando. Consiste em uma integração entre um banco de dados gerado a partir de uma imagem do Postgres por meio do Docker e o Kafka como sistema de mensageria para uma monitoração em tempo real da retirada ou recebimento de medicamentos de um estoque ficticio. Producer(Extrator dos dados do DB) -> Kafka (garantindo que a mensagem chegue) -> Consumer(Monitor em tempo real), atuando como um painel de monitoramento que lê as mensagens do tópico e exibe as entradas e saídas instantaneamente no terminal."""

consumer = KafkaConsumer(
    'teste', 
    bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
    group_id='monitor-hospitalar-v1',
    auto_offset_reset='earliest', # Lê tudo desde o início se ligar atrasado
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def limpar_tela():
    os.system('cls'if os.name == 'nt' else 'clear')

limpar_tela()
print("="*60)
print("CENTRAL DE MONITORAMENTO DA FARMÁCIA (TEMPO REAL)")
print("="*60)
print("Aguardando movimentação do banco de dados...\n")

try: 
    for msg in consumer:
        evento = msg.value

        # Extraindo os campos exatamente como vieram da tabela do Postgres
        registro_id = evento['id']
        hospital = evento['hospital_id']
        medicamento = evento['medicamento']
        tipo_mov = evento['tipo_movimento']
        qtd = evento['quantidade']
        data_hora = evento['data_registro']

        # Lógica de processamento e visualização no terminal
        if tipo_mov == "ENTRADA":
            # Simula a lógica de atualizar estoques para mais
            print(f" [ID: {registro_id:04d}] {data_hora}")
            print(f" RECEBIMENTO no {hospital}: Foram adicionadas {qtd} unidades de '{medicamento}'.\n")
        
        elif tipo_mov == "SAIDA":
            #Simula a logica de consumo diario
            print(f" [ID: {registro_id:04d}] {data_hora}")
            print(f" DISPENSA no {hospital}: Foram retiradas {qtd} unidades de '{medicamento}'.\n")

        
        consumer.commit()
except KeyboardInterrupt:
    print("\n Monitoramento encerrado pelo usuário.")
finally:
    consumer.close()
    print(" Conexão encerrada com segurança.")
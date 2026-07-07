import json
from kafka import KafkaProducer, KafkaConsumer
from src.config.settings import settings

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        client_id='simulador-saidas',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def get_kafka_consumer(topic: str, group_id: str = None):
    return KafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        # 'earliest' garante que mensagens publicadas antes do consumer estar ativo não sejam perdidas
        # um pedido publicado antes do scheduler/monitoramento estarem no ar
        # não pode simplesmente ser perdido.
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
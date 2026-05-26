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
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
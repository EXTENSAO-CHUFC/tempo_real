import json
from kafka import KafkaProducer, KafkaConsumer

def get_kafka_producer():
    """Retorna um Producer configurado para enviar mensagens em JSON."""
    return KafkaProducer(
        bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
        client_id='simulador-saidas',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def get_kafka_consumer(topic: str, group_id: str = None):
    """Retorna um Consumer configurado para escutar um tópico específico."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:19090', 'localhost:19091', 'localhost:19092'],
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
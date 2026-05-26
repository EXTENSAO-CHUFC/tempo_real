import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    #Configurações do PostgreSQL
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpassword")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "farmacia_db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
    
    # Monta a URL de conexão do SQLAlchemy automaticamente
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    #Configurações do Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    #Configurações do Kafka
    _kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19090,localhost:19091,localhost:19092")
    KAFKA_BOOTSTRAP_SERVERS = _kafka_servers.split(",")  # Transforma a string numa lista para o Kafka
    KAFKA_TOPIC_MOVIMENTACAO = os.getenv("KAFKA_TOPIC_MOVIMENTACAO", "teste")

settings = Settings()
from db.queries import popular_estoque_inicial
from src.utils.db import get_db_session
from src.utils.redis_client import get_redis_client


def run():
    db = get_db_session()
    redis_client= get_redis_client()
    try:
        print("⏳ Iniciando o abastecimento da farmácia...\n")
        popular_estoque_inicial(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
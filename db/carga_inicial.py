from db.connection import SessionLocal
from db.queries import popular_estoque_inicial

def run():
    db = SessionLocal()
    try:
        print("⏳ Iniciando o abastecimento da farmácia...\n")
        popular_estoque_inicial(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
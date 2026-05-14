from sqlalchemy.orm import Session
from db.models import EstoqueMedicamento
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def popular_estoque_inicial(db: Session):
    medicamentos_iniciais = [
        {"medicamento": "Dipirona Sódica 500mg", "estoque_atual": 1000, "estoque_maximo": 1000},
        {"medicamento": "Ibuprofeno 600mg", "estoque_atual": 500, "estoque_maximo": 500},
        {"medicamento": "Amoxicilina 500mg", "estoque_atual": 300, "estoque_maximo": 300},
        {"medicamento": "Soro Fisiológico 0.9%", "estoque_atual": 2000, "estoque_maximo": 2000},
        {"medicamento": "Clonazepam 2mg", "estoque_atual": 150, "estoque_maximo": 150}
    ]

    for item in medicamentos_iniciais:
        # duplicidade verificada
        existe = db.query(EstoqueMedicamento).filter(EstoqueMedicamento.medicamento == item["medicamento"]).first()
        
        if not existe:
            novo_medicamento = EstoqueMedicamento(**item)
            db.add(novo_medicamento)
            print(f"➕ Cadastrado: {item['medicamento']}")
        else:
            print(f"⏩ Ignorado (já existe): {item['medicamento']}")
            
    db.commit()

    print("⚡ Sincronizando dados com o cache em memória (Redis)...")
    todos_meds = db.query(EstoqueMedicamento).all()
    for med in todos_meds:
        redis_client.set(f"estoque:{med.id}", med.estoque_atual)
   
        
    print("\n📦 Operação de estoque e cache concluída com sucesso!")

   
import random
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from db.models import EstoqueMedicamento

def simular_requisicao(db: Session):
    # Pega apenas medicamentos que ainda têm estoque maior que zero
    medicamentos = db.query(EstoqueMedicamento).filter(EstoqueMedicamento.estoque_atual > 0).all()
    
    if not medicamentos:
        return None 

    escolhido = random.choice(medicamentos)
    qtd_retirada = random.randint(1, 15)
    
    # garante que não vai tentar tirar mais do que tem disponível
    if qtd_retirada > escolhido.estoque_atual:
        qtd_retirada = escolhido.estoque_atual

    return {
        "id_medicamento": escolhido.id,
        "medicamento": escolhido.medicamento,
        "tipo_movimento": "SAIDA",
        "quantidade": qtd_retirada,
        "hospital_id": "CH-01"
    }
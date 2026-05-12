from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from db.models import EstoqueMedicamento

def atualizar_estoque_banco(db: Session, id_medicamento: int, qtd_retirada: int):
    # Busca o medicamento pelo ID
    med = db.query(EstoqueMedicamento).filter(EstoqueMedicamento.id == id_medicamento).first()
    
    if med:
        med.estoque_atual -= qtd_retirada
        db.commit() 
        return True
        
    return False
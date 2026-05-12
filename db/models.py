from sqlalchemy import Column, Integer, String
from db.connection import Base


class EstoqueMedicamento(Base):
    __tablename__ = "estoque_medicamentos"

    id = Column(Integer, primary_key=True, index=True)
    medicamento = Column(String(100), nullable=False, unique=True)
    estoque_atual = Column(Integer, nullable=False)
    estoque_maximo = Column(Integer, nullable=False) 
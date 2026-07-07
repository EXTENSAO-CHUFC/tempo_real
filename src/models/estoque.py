import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Enum, ForeignKey, CheckConstraint, Boolean
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def agora_utc():
    return datetime.now(timezone.utc)


class TipoMovimentacao(enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    principio_ativo = Column(String(150), nullable=False)
    unidade_medida = Column(String(20), nullable=False)  
    estoque_minimo = Column(Integer, nullable=False, default=0)
    estoque_maximo = Column(Integer, nullable=False, default=200)  

    
    # Usado para simular, propositalmente, um medicamento que vai zerar (Clonazepam).
    bloqueio_reabastecimento = Column(Boolean, nullable=False, default=False)

    # Um medicamento -> muitos lotes (1:N)
    lotes = relationship(
        "Lote",
        back_populates="medicamento",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Medicamento(id={self.id}, nome='{self.nome}')>"


class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicamento_id = Column(
        Integer,
        ForeignKey("medicamentos.id", ondelete="CASCADE"),
        nullable=False
    )
    numero_lote = Column(String(50), nullable=False)
    data_validade = Column(Date, nullable=False)
    data_criacao = Column(DateTime, nullable=False, default=agora_utc)

    medicamento = relationship("Medicamento", back_populates="lotes")

    # Um lote -> muitas movimentações (1:N)
    movimentacoes = relationship(
        "Movimentacao",
        back_populates="lote",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("data_validade > '2000-01-01'", name="ck_validade_minima"),
    )

    def __repr__(self):
        return f"<Lote(id={self.id}, numero_lote='{self.numero_lote}')>"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column(
        Integer,
        ForeignKey("lotes.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False, default=agora_utc)
    origem_destino = Column(String(150), nullable=True)  # ex: 'Fornecedor X' ou 'Setor UTI'

    lote = relationship("Lote", back_populates="movimentacoes") 

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_quantidade_positiva"),
    )

    def __repr__(self):
        return f"<Movimentacao(id={self.id}, tipo={self.tipo}, qtd={self.quantidade})>"
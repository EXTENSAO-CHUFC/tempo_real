import random
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.models.estoque import Lote, Movimentacao, TipoMovimentacao


def _saldo_atual_lote(db: Session, lote_id: int) -> int:
    movimentacoes = db.query(Movimentacao).filter(Movimentacao.lote_id == lote_id).all()

    entradas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.ENTRADA)
    saidas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.SAIDA)

    return entradas - saidas


def simular_reabastecimento(db: Session, lote_id: int):
    """
    Calcula a entrada necessária para repor um lote específico até o
    estoque_maximo do seu medicamento. 
    """
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        return None

    saldo_atual = _saldo_atual_lote(db, lote.id)
    espaco_disponivel = lote.medicamento.estoque_maximo - saldo_atual

    if espaco_disponivel <= 0:
        return None

    return {
        "lote_id": lote.id,
        "medicamento": lote.medicamento.nome,
        "tipo_movimento": TipoMovimentacao.ENTRADA.value,
        "quantidade": espaco_disponivel,
        "origem_destino": "Fornecedor Farmacêutico Ceará Ltda (reabastecimento automático)",
    }


def simular_saida(db: Session):
    lotes = db.query(Lote).all()
    lotes_com_saldo = [(lote, _saldo_atual_lote(db, lote.id)) for lote in lotes]
    lotes_disponiveis = [(lote, saldo) for lote, saldo in lotes_com_saldo if saldo > 0]

    if not lotes_disponiveis:
        return None

    lote, saldo = random.choice(lotes_disponiveis)
    qtd_retirada = random.randint(1, 40)

    
    if qtd_retirada > saldo:
        qtd_retirada = saldo

    return {
        "lote_id": lote.id,
        "medicamento": lote.medicamento.nome,
        "tipo_movimento": TipoMovimentacao.SAIDA.value,
        "quantidade": qtd_retirada,
        "origem_destino": "Setor de Dispensação CH-UFC",
    }
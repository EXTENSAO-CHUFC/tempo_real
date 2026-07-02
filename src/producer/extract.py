import random
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.models.estoque import Lote, Movimentacao, TipoMovimentacao


def _saldo_atual_lote(db: Session, lote_id: int) -> int:
    """
    Calcula o saldo de um lote somando entradas e subtraindo saídas.
    Não existe mais um campo 'estoque_atual' — o saldo é sempre
    derivado das movimentações já registradas (princípio da 3FN:
    nenhum dado redundante, tudo calculado a partir da fonte única).
    """
    movimentacoes = db.query(Movimentacao).filter(Movimentacao.lote_id == lote_id).all()

    entradas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.ENTRADA)
    saidas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.SAIDA)

    return entradas - saidas


def simular_entrada(db: Session):
    lotes = db.query(Lote).all()

    lotes_com_espaco = []
    for lote in lotes:
        saldo_atual = _saldo_atual_lote(db, lote.id)
        espaco_disponivel = lote.medicamento.estoque_maximo - saldo_atual
        if espaco_disponivel > 0:
            lotes_com_espaco.append((lote, espaco_disponivel))

    if not lotes_com_espaco:
        return None

    lote, espaco_disponivel = random.choice(lotes_com_espaco)

    # sorteia entre 10 e 50 como antes, nunca além do espaço que falta
    teto_sorteio = min(50, espaco_disponivel)
    piso_sorteio = min(10, teto_sorteio)
    qtd_entrada = random.randint(piso_sorteio, teto_sorteio)

    return {
        "lote_id": lote.id,
        "medicamento": lote.medicamento.nome,
        "tipo_movimento": TipoMovimentacao.ENTRADA.value,
        "quantidade": qtd_entrada,
        "origem_destino": "Fornecedor Farmacêutico Ceará Ltda",
    }


def simular_saida(db: Session):
    lotes = db.query(Lote).all()
    lotes_com_saldo = [(lote, _saldo_atual_lote(db, lote.id)) for lote in lotes]
    lotes_disponiveis = [(lote, saldo) for lote, saldo in lotes_com_saldo if saldo > 0]

    if not lotes_disponiveis:
        return None

    lote, saldo = random.choice(lotes_disponiveis)
    qtd_retirada = random.randint(1, 40)

    # garante que não retira mais do que o saldo calculado do lote
    if qtd_retirada > saldo:
        qtd_retirada = saldo

    return {
        "lote_id": lote.id,
        "medicamento": lote.medicamento.nome,
        "tipo_movimento": TipoMovimentacao.SAIDA.value,
        "quantidade": qtd_retirada,
        "origem_destino": "Setor de Dispensação CH-UFC",
    }
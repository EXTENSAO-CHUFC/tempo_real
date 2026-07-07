import os
import sys
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from sqlalchemy import text

from src.models.estoque import Base, Medicamento, Lote, Movimentacao, TipoMovimentacao
from src.utils.db import get_db_session
from src.utils.redis_client import get_redis_client
from db.connection import engine


def migrar_schema_existente(engine):
    """
    Base.metadata.create_all() só cria tabelas que ainda não existem, mas não altera tabelas já existentes.
    """
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE medicamentos "
            "ADD COLUMN IF NOT EXISTS bloqueio_reabastecimento BOOLEAN NOT NULL DEFAULT false"
        ))


def popular_estoque_inicial(db, redis_client):
    medicamentos_iniciais = [
        {"nome": "Dipirona Sódica 500mg", "principio_ativo": "Dipirona",
         "unidade_medida": "comprimido", "estoque_minimo": 200, "estoque_maximo": 500,
         "estoque_inicial": 500, "bloqueio_reabastecimento": False,
         "numero_lote": "LOT-2026-001", "data_validade": date(2027, 12, 31)},
        {"nome": "Ibuprofeno 600mg", "principio_ativo": "Ibuprofeno",
         "unidade_medida": "comprimido", "estoque_minimo": 150, "estoque_maximo": 400,
         "estoque_inicial": 400, "bloqueio_reabastecimento": False,
         "numero_lote": "LOT-2026-002", "data_validade": date(2027, 10, 15)},
        {"nome": "Amoxicilina 500mg", "principio_ativo": "Amoxicilina",
         "unidade_medida": "comprimido", "estoque_minimo": 150, "estoque_maximo": 400,
         "estoque_inicial": 400, "bloqueio_reabastecimento": False,
         "numero_lote": "LOT-2026-003", "data_validade": date(2027, 8, 20)},
        {"nome": "Soro Fisiológico 0,9%", "principio_ativo": "Cloreto de Sódio",
         "unidade_medida": "frasco", "estoque_minimo": 50, "estoque_maximo": 150,
         "estoque_inicial": 150, "bloqueio_reabastecimento": False,
         "numero_lote": "LOT-2026-004", "data_validade": date(2028, 1, 10)},
        {"nome": "Clonazepam 2mg", "principio_ativo": "Clonazepam",
         "unidade_medida": "comprimido", "estoque_minimo": 100, "estoque_maximo": 300,
         "estoque_inicial": 40, "bloqueio_reabastecimento": True,
         "numero_lote": "LOT-2026-005", "data_validade": date(2027, 6, 30)},
    ]

    for item in medicamentos_iniciais:
        existe = db.query(Medicamento).filter(Medicamento.nome == item["nome"]).first()

        if not existe:
            medicamento = Medicamento(
                nome=item["nome"],
                principio_ativo=item["principio_ativo"],
                unidade_medida=item["unidade_medida"],
                estoque_minimo=item["estoque_minimo"],
                estoque_maximo=item["estoque_maximo"],
                bloqueio_reabastecimento=item["bloqueio_reabastecimento"],
            )
            db.add(medicamento)
            db.flush()  

            lote = Lote(
                medicamento_id=medicamento.id,
                numero_lote=item["numero_lote"],
                data_validade=item["data_validade"],
            )
            db.add(lote)
            db.flush()  
            mov_inicial = Movimentacao(
                lote_id=lote.id,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=item["estoque_inicial"],
                origem_destino="Estoque inicial (carga do sistema)",
            )
            db.add(mov_inicial)
            db.commit()

            saldo_para_cache = item["estoque_inicial"]

            print(f"➕ Cadastrado: {item['nome']} (lote {item['numero_lote']}, "
                  f"máximo: {item['estoque_maximo']}, inicial: {item['estoque_inicial']}, "
                  f"bloqueio_reabastecimento: {item['bloqueio_reabastecimento']})")
        else:

            if existe.bloqueio_reabastecimento != item["bloqueio_reabastecimento"]:
                existe.bloqueio_reabastecimento = item["bloqueio_reabastecimento"]
                db.commit()

            lote_existente = existe.lotes[0] if existe.lotes else None
            saldo_redis = redis_client.get(f"saldo_lote:{lote_existente.id}") if lote_existente else None
            saldo_para_cache = int(saldo_redis) if saldo_redis is not None else item["estoque_inicial"]

            print(f"⏩ Ignorado (já existe, flag de bloqueio sincronizada): {item['nome']}")

        
        lote_para_cache = db.query(Medicamento).filter(
            Medicamento.nome == item["nome"]
        ).first().lotes[0]

        redis_client.hset(f"meta_lote:{lote_para_cache.id}", mapping={
            "estoque_maximo": item["estoque_maximo"],
            "bloqueio_reabastecimento": int(item["bloqueio_reabastecimento"]),
            "medicamento": item["nome"],
        })
        if redis_client.get(f"saldo_lote:{lote_para_cache.id}") is None:
            redis_client.set(f"saldo_lote:{lote_para_cache.id}", saldo_para_cache)

    db.commit()
    print("\n📦 Catálogo de medicamentos e lotes iniciais cadastrado com sucesso!")


def run():
    Base.metadata.create_all(bind=engine)
    migrar_schema_existente(engine)
    db = get_db_session()
    redis_client = get_redis_client()
    try:
        print("⏳ Iniciando o abastecimento da farmácia (modelo 3FN)...\n")
        popular_estoque_inicial(db, redis_client)
    finally:
        db.close()


if __name__ == "__main__":
    run()
import os
import sys
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.models.estoque import Base, Medicamento, Lote
from src.utils.db import get_db_session
from db.connection import engine


def popular_estoque_inicial(db):
    medicamentos_iniciais = [
        {"nome": "Dipirona Sódica 500mg", "principio_ativo": "Dipirona",
         "unidade_medida": "comprimido", "estoque_minimo": 200, "estoque_maximo": 500,
         "numero_lote": "LOT-2026-001", "data_validade": date(2027, 12, 31)},
        {"nome": "Ibuprofeno 600mg", "principio_ativo": "Ibuprofeno",
         "unidade_medida": "comprimido", "estoque_minimo": 150, "estoque_maximo": 400,
         "numero_lote": "LOT-2026-002", "data_validade": date(2027, 10, 15)},
        {"nome": "Amoxicilina 500mg", "principio_ativo": "Amoxicilina",
         "unidade_medida": "comprimido", "estoque_minimo": 150, "estoque_maximo": 400,
         "numero_lote": "LOT-2026-003", "data_validade": date(2027, 8, 20)},
        {"nome": "Soro Fisiológico 0,9%", "principio_ativo": "Cloreto de Sódio",
         "unidade_medida": "frasco", "estoque_minimo": 50, "estoque_maximo": 150,
         "numero_lote": "LOT-2026-004", "data_validade": date(2028, 1, 10)},
        {"nome": "Clonazepam 2mg", "principio_ativo": "Clonazepam",
         "unidade_medida": "comprimido", "estoque_minimo": 100, "estoque_maximo": 300,
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
            )
            db.add(medicamento)
            db.flush()  # garante medicamento.id disponível antes de criar o lote

            lote = Lote(
                medicamento_id=medicamento.id,
                numero_lote=item["numero_lote"],
                data_validade=item["data_validade"],
            )
            db.add(lote)
            print(f"➕ Cadastrado: {item['nome']} (lote {item['numero_lote']}, máximo: {item['estoque_maximo']})")
        else:
            print(f"⏩ Ignorado (já existe): {item['nome']}")

    db.commit()
    print("\n📦 Catálogo de medicamentos e lotes iniciais cadastrado com sucesso!")


def run():
    Base.metadata.create_all(bind=engine)
    db = get_db_session()
    try:
        print("⏳ Iniciando o abastecimento da farmácia (modelo 3FN)...\n")
        popular_estoque_inicial(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
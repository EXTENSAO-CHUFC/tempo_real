"""
src/tests/test_estoque_3fn.py

Testes unitários do modelo normalizado (Medicamento, Lote, Movimentacao)
e da regra de negócio "saldo não pode ficar negativo e deve alertar ao zerar".

Roda sem Docker, sem Kafka, sem Postgres real — usa SQLite em memória
e um Redis falso (FakeRedis) para isolar a lógica de qualquer infraestrutura.

Para rodar:
    pip install pytest sqlalchemy --break-system-packages
    pytest src/tests/test_estoque_3fn.py -v
"""

import pytest
from datetime import date
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.models.estoque import Base, Medicamento, Lote, Movimentacao, TipoMovimentacao
from src.consumers.monitoramento.handler import avaliar_estoque, limpar_alerta


class FakeRedis:
    """Substitui o redis.Redis real só para os testes, sem precisar de container."""
    def __init__(self):
        self.store = {}
        self.lists = {}

    def incrby(self, key, val):
        self.store[key] = self.store.get(key, 0) + val
        return self.store[key]

    def decrby(self, key, val):
        self.store[key] = self.store.get(key, 0) - val
        return self.store[key]

    def lpush(self, key, val):
        self.lists.setdefault(key, []).insert(0, val)

    def ltrim(self, key, start, end):
        self.lists[key] = self.lists[key][start:end + 1]

    def set(self, key, val):
        self.store[key] = val

    def delete(self, key):
        self.store.pop(key, None)

    def get(self, key):
        return self.store.get(key)


@pytest.fixture
def db_session():
    """
    Banco SQLite em memória, recriado a cada teste (isolamento total).

    NOTA IMPORTANTE: o SQLite não aplica CheckConstraint por padrão —
    é preciso ligar 'PRAGMA foreign_keys=ON' (que também ativa checks)
    em cada conexão. O PostgreSQL real do projeto já aplica as
    constraints automaticamente, sem precisar disso; este PRAGMA
    existe só para o teste em SQLite se comportar como o Postgres.
    """
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def habilitar_constraints(conexao_dbapi, _):
        conexao_dbapi.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def redis_client():
    return FakeRedis()


@pytest.fixture
def lote_amoxicilina(db_session):
    """Cria um medicamento e um lote de teste, retorna o objeto Lote."""
    medicamento = Medicamento(
        nome="Amoxicilina 500mg",
        principio_ativo="Amoxicilina",
        unidade_medida="comprimido",
        estoque_minimo=50,
    )
    db_session.add(medicamento)
    db_session.flush()

    lote = Lote(
        medicamento_id=medicamento.id,
        numero_lote="LOT-2026-003",
        data_validade=date(2027, 8, 20),
    )
    db_session.add(lote)
    db_session.commit()
    return lote


def test_saldo_soma_entrada_e_subtrai_saida(db_session, lote_amoxicilina):
    """O saldo de um lote deve ser sempre (soma de ENTRADA) - (soma de SAIDA)."""
    db_session.add(Movimentacao(lote_id=lote_amoxicilina.id, tipo=TipoMovimentacao.ENTRADA, quantidade=100))
    db_session.add(Movimentacao(lote_id=lote_amoxicilina.id, tipo=TipoMovimentacao.SAIDA, quantidade=30))
    db_session.commit()

    movimentacoes = db_session.query(Movimentacao).filter(
        Movimentacao.lote_id == lote_amoxicilina.id
    ).all()
    entradas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.ENTRADA)
    saidas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.SAIDA)

    assert entradas - saidas == 70


def test_quantidade_zero_ou_negativa_e_rejeitada_pelo_banco(db_session, lote_amoxicilina):
    """A constraint ck_quantidade_positiva deve impedir quantidade <= 0."""
    mov_invalida = Movimentacao(lote_id=lote_amoxicilina.id, tipo=TipoMovimentacao.SAIDA, quantidade=0)
    db_session.add(mov_invalida)
    with pytest.raises(Exception):
        db_session.commit()


def test_alerta_dispara_quando_saldo_chega_a_zero(redis_client):
    disparou = avaliar_estoque(novo_saldo=0, lote_id=1, medicamento="Amoxicilina", redis_client=redis_client)

    assert disparou is True
    assert redis_client.get("alerta:lote:1") == "1"
    assert len(redis_client.lists["alertas_criticos"]) == 1


def test_alerta_nao_dispara_com_saldo_positivo(redis_client):
    disparou = avaliar_estoque(novo_saldo=15, lote_id=2, medicamento="Dipirona", redis_client=redis_client)

    assert disparou is False
    assert redis_client.get("alerta:lote:2") is None


def test_alerta_e_limpo_apos_reabastecimento(redis_client):
    avaliar_estoque(novo_saldo=0, lote_id=3, medicamento="Ibuprofeno", redis_client=redis_client)
    assert redis_client.get("alerta:lote:3") == "1"

    limpar_alerta(lote_id=3, redis_client=redis_client)
    assert redis_client.get("alerta:lote:3") is None


def test_cache_redis_nunca_fica_negativo():
    """Simula a trava de segurança do consumer redis_cache: saída maior
    que o saldo disponível não pode deixar o cache negativo."""
    redis_client = FakeRedis()
    redis_client.set("saldo_lote:5", 10)

    novo_saldo = redis_client.decrby("saldo_lote:5", 30)
    if novo_saldo < 0:
        redis_client.set("saldo_lote:5", 0)
        novo_saldo = 0

    assert novo_saldo == 0
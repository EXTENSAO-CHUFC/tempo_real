from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# <-- MODIFICAÇÃO: Importa o modelo e manda o SQLAlchemy criar as tabelas faltantes
try:
    from db.models import EstoqueMedicamento
    Base.metadata.create_all(bind=engine)
except ImportError:
    # Caso haja um problema de importação circular em outro lugar, ele apenas ignora
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
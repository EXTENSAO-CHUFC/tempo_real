from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

try:
    from src.models.estoque import Base
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
from db.connection import SessionLocal

def get_db_session():
    """Retorna uma nova sessão do SQLAlchemy para o PostgreSQL."""
    return SessionLocal()
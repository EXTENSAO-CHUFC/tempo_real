import os
import sys
from db.connection import engine, Base
from db.models import EstoqueMedicamento 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def iniciar_banco():
    print("⏳ Conectando ao PostgreSQL...")
    
    # checa se o .env foi lido
    if os.getenv("POSTGRES_DB") is None:
        print("❌ ERRO: O arquivo .env não foi encontrado ou não carregou!")
        return
        
    print(f"🔌 Conectado ao banco: {os.getenv('POSTGRES_DB')} no host {os.getenv('POSTGRES_HOST')}")

    # cria todas as tabelas que herdam de 'Base'
    Base.metadata.create_all(bind=engine)
    
    print("✅ Banco de dados estruturado com sucesso no padrão MVC!")

if __name__ == "__main__":
    iniciar_banco()
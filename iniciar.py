import os
import time
import webbrowser
import platform

def main():
    print("🚀 Iniciando a infraestrutura da Farmácia CH-UFC (Docker)...")
    
    # 1. Sobe tudo silenciosamente em background (-d)
    os.system("docker compose up -d")
    
    print("\n⏳ Aguardando os serviços aquecerem (10 segundos)...")
    # Dá tempo para o Kafka e o Postgres respirarem
    time.sleep(10)
    
    print("🌐 Redirecionando para o Dashboard...")
    url = "http://localhost:8501"
    
    # Tenta abrir o navegador (Trata a diferença entre Windows puro e WSL)
    if "microsoft-standard" in platform.uname().release.lower():
        # Estamos dentro do WSL
        os.system(f"explorer.exe {url} > /dev/null 2>&1")
    else:
        # Estamos num sistema normal
        webbrowser.open(url)
        
    print("\n✅ Sistema rodando perfeitamente em background!")
    print("👉 Para desligar tudo depois, digite: docker compose down")
    print("👉 Para ver os logs dos robôs, digite: docker compose logs -f producer_simulador consumer_redis")

if __name__ == "__main__":
    main()
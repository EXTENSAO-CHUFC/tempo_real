import subprocess
import time
import os
import sys

def main():
    print("===================================================")
    print(" Iniciando o Sistema de Monitoramento CH-UFC...")
    print("===================================================\n")

    
    print("[1/5] 🐳 Subindo Bancos e Kafka via Docker...")
    subprocess.run(["docker-compose", "up", "-d"])

    
    print("\n[2/5] ⏳ Aguardando 10 segundos para a infraestrutura estabilizar...")
    time.sleep(10)


    print("\n [3/5] Criando a tabela do estoque de remédios...")
    subprocess.run([sys.executable, "-m", "db.main"])

    
    print("\n[4/5] 📦 Preenchendo o estoque inicial...")
    subprocess.run([sys.executable, "-m", "db.carga_inicial"])

    print("\n[5/5] 🖥️ Abrindo Dashboard, Producer e Consumer em novos terminais...")
    
    python_exe = sys.executable 
    
    
    os.system(f'start "Consumer Redis (CH-UFC)" cmd /k "{python_exe} src/consumers/redis_cache/main.py"')
    
    os.system(f'start "Producer Simulador (CH-UFC)" cmd /k "{python_exe} -m src.producer.main"')
    
    os.system(f'start "Dashboard (CH-UFC)" cmd /k "{python_exe} -m streamlit run src/dashboard/app.py"')

    print("\n✅ Tudo rodando! As 3 janelas devem ter aparecido na sua tela.")
    print("O seu navegador vai abrir o Dashboard em instantes.")
    print("Você pode fechar esta janela principal ou deixá-la aberta.")

if __name__ == "__main__":
    main()
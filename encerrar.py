import subprocess

def main():
    print("===================================================")
    print("🛑 Desligando o Sistema de Monitoramento CH-UFC...")
    print("===================================================\n")

    print("[1/2] 🐳 Encerrando os bancos e a mensageria no Docker...")
    
    subprocess.run(["docker-compose", "down"])

    print("\n[2/2] ✅ Infraestrutura desligada com sucesso!")
    print("\n⚠️  Lembre-se de fechar manualmente as janelas pretas (terminais) do Dashboard, Producer e Consumer que ficaram abertas.")
    print("Até a próxima! 👋\n")

if __name__ == "__main__":
    main()
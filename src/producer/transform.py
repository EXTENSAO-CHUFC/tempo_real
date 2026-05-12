from datetime import datetime

def preparar_mensagem_kafka(evento_bruto: dict):
    # Cria uma cópia do evento e adiciona o carimbo de tempo exato da simulação
    evento_transformado = evento_bruto.copy()
    evento_transformado["data_registro"] = datetime.now().isoformat()
    
    return evento_transformado
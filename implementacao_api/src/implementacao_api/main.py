import requests
import json 
import pandas as pd
import numpy as np
from datetime import date

#url = "https://prod.huwc.ufc.br/aghu_chufc_api/cirurgias?"
#filial=huwc&dataInicial=2025-01-01&dataFinal=2025-01-10"

#dados_disponiveis = dados.json()
#print("filial:", dados_disponiveis["filial"])

#print("Status code:", dados.status_code)
#print("Content-type:", dados.headers.get("Content-Type"))

#data = dados.json()
#print(data)


dados = "https://prod.huwc.ufc.br/aghu_chufc_api/cirurgias?"
params = {"filial": "huwc",
          "dataInicial":date(2025,1,1),
          "dataFinal":date(2025,1,10)}
headers = {
    "Authorization": f"Bearer {"c7ce9fdb80704e1ef42d17e1abd02836cd1d2ae1fa0bbb7fb71c2af23c9343c1"}"
}



resposta = requests.get(url="https://prod.huwc.ufc.br/aghu_chufc_api/cirurgias?", params=params, headers=headers)

print("Final URL:", resposta.url)

resposta.raise_for_status()

dados_retornados = resposta.json()
print("Dados da API:", dados_retornados)

dados_api = resposta.json()
print("Cirurgias realizadas:", dados_api)

tabela_cirurgias = pd.DataFrame(dados_api)
print("Tabela de Cirurgias:")
#print(tabela_cirurgias)
listaColunas = ["especialidade","dthrFimCirg"]
print(tabela_cirurgias[listaColunas])

 


#tabela_cirurgias.to_csv('filename.csv', index=False)



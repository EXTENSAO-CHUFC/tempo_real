import requests
import json 
import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt

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
#print("Tabela de Cirurgias:")
#print(tabela_cirurgias.info())
tabela_cirurgias.to_excel('dados_da_API.xlsx', index=False)


#Mostrar um grafico ao rodar o codigo.
#tabela_cirurgias.hist()
#plt.show()


#Copia segura para testar a limpeza e tratamento dos dados
df_analise = tabela_cirurgias.copy()

colunas_de_data = ['data', 'dthrPrevInicio', 'dthrPrevFim', 'dthrInicioAnest', 
                   'dthrInicioCirg', 'dthrFimAnest', 'dthrFimCirg', 'criadoEm']

for coluna in colunas_de_data:
    df_analise[coluna] = pd.to_datetime(df_analise[coluna], errors='coerce')


tabela_anonimizada = df_analise.drop(columns=['pacCodigo'])
#tabela_anonimizada.to_excel("cirurgias_aghu_tratado.xlsx", index=False)

print("\n[2] Situação das Cirurgias:")
print(df_analise['situacao'].value_counts())

df_analise['duracao das cirurgias'] = (df_analise['dthrFimCirg'] - df_analise['dthrInicioCirg']).dt.total_seconds() / 60

print(df_analise)

cirurgias_validas = df_analise[df_analise['duracao das cirurgias']>0]




plt.figure(figsize=(10, 6))

# Pega o Top 10 especialidades que mais operaram e cria um gráfico de barras azuis
df_analise['especialidade'].value_counts().head(10).plot(kind='bar', color='#4C72B0')

plt.title('Top 10 Especialidades com Maior Volume de Cirurgias', fontsize=14)
plt.xlabel('Especialidade Médica', fontsize=12)
plt.ylabel('Quantidade de Cirurgias', fontsize=12)

plt.xticks(rotation=45, ha='right')

plt.tight_layout()

plt.show()

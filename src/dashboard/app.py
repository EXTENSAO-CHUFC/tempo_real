import streamlit as st
import pandas as pd
import sys
import os
import time
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from db.connection import SessionLocal
from db.models import EstoqueMedicamento


st.set_page_config(page_title="Monitor Farmácia CH-UFC", page_icon="🏥", layout="wide")

def carregar_dados():
    """Conecta no Postgres para dados estáticos e no REDIS para os dados em tempo real."""
    db = SessionLocal()
    try:
        medicamentos = db.query(EstoqueMedicamento).all()
        dados = []
        for med in medicamentos:
            estoque_redis = redis_client.get(f"estoque:{med.id}")
            if estoque_redis is not None:
                estoque_atual = int(estoque_redis)
            else:
                estoque_atual = med.estoque_atual
                
            dados.append({
                "ID": med.id,
                "Medicamento": med.medicamento,
                "Estoque Atual": estoque_atual, 
                "Estoque Máximo": med.estoque_maximo
            })
        return pd.DataFrame(dados)
    finally:
        db.close()

def aplicar_regra_semaforo(linha):
    porcentagem = linha['Estoque Atual'] / linha['Estoque Máximo']
    
    if porcentagem > 0.70:
        status = "🟢 Seguro"
    elif porcentagem >= 0.10:
        status = "🟡 Atenção"
    else:
        status = "🔴 Crítico"
        
    return pd.Series([f"{porcentagem*100:.1f}%", status])


st.title("🏥 Central de Monitoramento de Estoque")
st.markdown("Visão em tempo real da disponibilidade de medicamentos na farmácia do CH-UFC.")


if st.button("🔄 Atualizar Dados Agora"):
    st.toast("Buscando dados mais recentes do banco...")


df_estoque = carregar_dados()

if not df_estoque.empty:
    df_estoque[['Ocupação (%)', 'Status']] = df_estoque.apply(aplicar_regra_semaforo, axis=1)

    
    qtd_critico = len(df_estoque[df_estoque['Status'] == "🔴 Crítico"])
    qtd_atencao = len(df_estoque[df_estoque['Status'] == "🟡 Atenção"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tipos de Medicamentos", len(df_estoque))
    col2.metric("Medicamentos em Atenção", qtd_atencao)
    col3.metric("🚨 Alertas Críticos", qtd_critico)

    st.divider()

    st.subheader("📦 Detalhamento do Estoque")
    st.dataframe(df_estoque, use_container_width=True, hide_index=True)

else:
    st.warning("Nenhum medicamento encontrado no banco de dados.")


time.sleep(4)
st.rerun()
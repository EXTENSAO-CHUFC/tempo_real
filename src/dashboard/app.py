import streamlit as st
import sys
import os
import pandas as pd
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime
from src.utils.db import get_db_session
from src.utils.redis_client import get_redis_client
from db.models import EstoqueMedicamento

st.set_page_config(page_title="Monitor Farmácia CH-UFC", page_icon="🏥", layout="wide")

def carregar_dados():
    db = get_db_session()
    redis_client = get_redis_client()
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
    maximo = linha['Estoque Máximo']
    porcentagem = (linha['Estoque Atual'] / maximo) if maximo > 0 else 0
    
    if porcentagem > 0.70:
        status = "🟢 Seguro"
        peso = 3
    elif porcentagem >= 0.10:
        status = "🟡 Atenção"
        peso = 2
    else:
        status = "🔴 Crítico"
        peso = 1
        
    return pd.Series([f"{porcentagem*100:.1f}%", status, peso, porcentagem])


#Logo e a Timestamp de atualização

def main():
    with st.sidebar:
        try:
            st.image("src/utils/logo-huwc-Photoroom.png", use_container_width=True)
        except Exception:
            st.markdown("### 🏥 Complexo Hospitalar UFC")
        
        st.divider()
        st.info("📡 Operando em Tempo Real (Kafka + Redis)")
        
        hora_atual = datetime.now().strftime("%H:%M:%S")
        st.success(f"⏱️ Última atualização:\n\n**{hora_atual}**")


    st.title("🏥 Central de Monitoramento de Estoque")
    st.markdown("Visão em tempo real da disponibilidade de medicamentos na farmácia do CH-UFC.")

    if st.button("🔄 Atualizar Dados Agora"):
        st.toast("Buscando dados mais recentes do banco...")

    df_estoque = carregar_dados()

    if not df_estoque.empty:
        df_estoque[['Ocupação (%)', 'Status', 'Peso_Ordem', 'Valor_Pct']] = df_estoque.apply(aplicar_regra_semaforo, axis=1)

        df_estoque = df_estoque.sort_values(by=['Peso_Ordem', 'Valor_Pct'], ascending=[True, True])
        
        df_estoque = df_estoque.drop(columns=['Peso_Ordem', 'Valor_Pct'])
        
        # Calcula as métricas
        qtd_critico = len(df_estoque[df_estoque['Status'] == "🔴 Crítico"])
        qtd_atencao = len(df_estoque[df_estoque['Status'] == "🟡 Atenção"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Tipos de Medicamentos", len(df_estoque))
        col2.metric("Medicamentos em Atenção", qtd_atencao)
        
        
        delta_msg = f"-{qtd_critico} faltas urgentes" if qtd_critico > 0 else "Estoque Normal"
        col3.metric("🚨 Alertas Críticos", qtd_critico, delta=delta_msg, delta_color="inverse")

        st.divider()

        st.subheader("📦 Detalhamento do Estoque")
        st.dataframe(df_estoque, use_container_width=True, hide_index=True)

    else:
        st.warning("Nenhum medicamento encontrado no banco de dados.")

    time.sleep(4)
    st.rerun()

if __name__ == "__main__":
    main()
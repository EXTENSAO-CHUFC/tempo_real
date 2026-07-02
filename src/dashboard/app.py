import streamlit as st
import sys
import os
import pandas as pd
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime
from sqlalchemy.exc import ProgrammingError, OperationalError
from src.utils.db import get_db_session
from src.utils.redis_client import get_redis_client
from src.models.estoque import Medicamento, Lote, Movimentacao, TipoMovimentacao

st.set_page_config(page_title="Monitor Farmácia CH-UFC", page_icon="🏥", layout="wide")


def _saldo_lote_postgres(db, lote_id: int) -> int:
    """
    Fallback para quando o Redis ainda não tem o saldo de um lote em cache
    (ex: logo após o sistema subir). Calcula direto pela soma das
    movimentações já gravadas — a mesma lógica usada no producer/extract.py.
    """
    movimentacoes = db.query(Movimentacao).filter(Movimentacao.lote_id == lote_id).all()
    entradas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.ENTRADA)
    saidas = sum(m.quantidade for m in movimentacoes if m.tipo == TipoMovimentacao.SAIDA)
    return entradas - saidas


def carregar_dados():
    db = get_db_session()
    redis_client = get_redis_client()
    try:
        lotes = db.query(Lote).all()
        dados = []
        for lote in lotes:
            saldo_redis = redis_client.get(f"saldo_lote:{lote.id}")
            if saldo_redis is not None:
                saldo_atual = int(saldo_redis)
            else:
                saldo_atual = _saldo_lote_postgres(db, lote.id)

            dados.append({
                "Lote ID": lote.id,
                "Número do Lote": lote.numero_lote,
                "Medicamento": lote.medicamento.nome,
                "Saldo Atual": saldo_atual,
                "Estoque Mínimo": lote.medicamento.estoque_minimo,
                "Estoque Máximo": lote.medicamento.estoque_maximo,
                "Validade": lote.data_validade.strftime("%d/%m/%Y"),
            })
        return pd.DataFrame(dados)
    except (ProgrammingError, OperationalError):
        db.rollback()
        return None
    finally:
        db.close()


def carregar_feed_tempo_real():
    """Busca os últimos eventos de ENTRADA e SAÍDA inseridos na lista do Redis."""
    redis_client = get_redis_client()
    logs = redis_client.lrange("feed_movimentacoes", 0, -1)

    if not logs:
        return pd.DataFrame()

    dados = [json.loads(log) for log in logs]
    return pd.DataFrame(dados)


def carregar_alertas_criticos():
    """Busca os últimos alertas de lote zerado, gravados pelo consumer de monitoramento."""
    redis_client = get_redis_client()
    alertas = redis_client.lrange("alertas_criticos", 0, -1)

    if not alertas:
        return pd.DataFrame()

    dados = [json.loads(a) for a in alertas]
    return pd.DataFrame(dados)


def aplicar_regra_semaforo(linha):
    minimo = linha['Estoque Mínimo']
    maximo = linha['Estoque Máximo']
    saldo = linha['Saldo Atual']

    # Status do semáforo continua relativo ao mínimo (crítico = perto de faltar)
    porcentagem_minimo = (saldo / minimo) if minimo > 0 else 0

    if porcentagem_minimo > 1.5:
        status = "🟢 Seguro"
        peso = 3
    elif porcentagem_minimo >= 1.0:
        status = "🟡 Atenção"
        peso = 2
    else:
        status = "🔴 Crítico"
        peso = 1

    # % de ocupação exibida é relativa ao máximo (capacidade física do lote)
    porcentagem_ocupacao = (saldo / maximo) if maximo > 0 else 0

    return pd.Series([f"{porcentagem_ocupacao*100:.0f}%", status, peso, porcentagem_minimo])


def colorir_tipo_movimento(valor):
    """Aplica cor de fundo na célula 'Tipo' do feed: verde para entrada, vermelho para saída."""
    if valor == "ENTRADA":
        return "background-color: #d1f5d3; color: #0a5c1f"
    elif valor == "SAIDA":
        return "background-color: #fbd6d6; color: #7a1212"
    return ""


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
    st.markdown("Visão em tempo real das entradas e saídas de medicamentos na farmácia do CH-UFC, por lote.")

    if st.button("🔄 Atualizar Dados Agora"):
        st.toast("Buscando dados mais recentes do banco...")

    df_estoque = carregar_dados()

    if df_estoque is None:
        st.warning("⏳ Aguardando a inicialização do banco de dados e a criação das tabelas...")
        time.sleep(4)
        st.rerun()
        return

    if not df_estoque.empty:
        df_estoque[['Ocupação (%)', 'Status', 'Peso_Ordem', 'Valor_Pct']] = df_estoque.apply(aplicar_regra_semaforo, axis=1)
        df_estoque = df_estoque.sort_values(by=['Peso_Ordem', 'Valor_Pct'], ascending=[True, True])
        df_estoque = df_estoque.drop(columns=['Peso_Ordem', 'Valor_Pct'])

        qtd_critico = len(df_estoque[df_estoque['Status'] == "🔴 Crítico"])
        qtd_atencao = len(df_estoque[df_estoque['Status'] == "🟡 Atenção"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Lotes Monitorados", len(df_estoque))
        col2.metric("Lotes em Atenção", qtd_atencao)

        delta_msg = f"-{qtd_critico} lotes urgentes" if qtd_critico > 0 else "Estoque Normal"
        col3.metric("🚨 Alertas Críticos", qtd_critico, delta=delta_msg, delta_color="inverse")

        st.divider()

        st.subheader("📦 Detalhamento do Estoque por Lote")
        st.dataframe(df_estoque, use_container_width=True, hide_index=True)

        st.divider()

        # --- Feed em tempo real de ENTRADAS e SAÍDAS ---
        st.subheader("⏱️ Movimentações em Tempo Real (Entradas e Saídas)")
        df_feed = carregar_feed_tempo_real()

        if not df_feed.empty:
            qtd_entradas = len(df_feed[df_feed['Tipo'] == 'ENTRADA'])
            qtd_saidas = len(df_feed[df_feed['Tipo'] == 'SAIDA'])

            col_e, col_s = st.columns(2)
            col_e.metric("🟢 Entradas recentes", qtd_entradas)
            col_s.metric("🔴 Saídas recentes", qtd_saidas)

            st.dataframe(
                df_feed.style.map(colorir_tipo_movimento, subset=['Tipo']),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Horário": st.column_config.TextColumn("Horário", width="small"),
                    "Lote": st.column_config.NumberColumn("Lote ID", width="small"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                    "Quantidade": st.column_config.NumberColumn("Qtd (un.)", width="small"),
                    "Medicamento": st.column_config.TextColumn("Medicamento", width="large"),
                }
            )
        else:
            st.info("Aguardando novas movimentações na farmácia...")

        st.divider()

        # --- Alertas de lote zerado ---
        st.subheader("🚨 Alertas de Estoque Zerado")
        df_alertas = carregar_alertas_criticos()

        if not df_alertas.empty:
            st.error(f"⚠️ {len(df_alertas)} alerta(s) de estoque crítico registrados.")
            st.dataframe(
                df_alertas,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "hora": st.column_config.TextColumn("Horário", width="small"),
                    "lote_id": st.column_config.NumberColumn("Lote ID", width="small"),
                    "medicamento": st.column_config.TextColumn("Medicamento", width="large"),
                    "saldo": st.column_config.NumberColumn("Saldo", width="small"),
                }
            )
        else:
            st.success("Nenhum lote zerado no momento.")

    else:
        st.warning("Nenhum lote encontrado no banco de dados.")

    time.sleep(4)
    st.rerun()


if __name__ == "__main__":
    main()
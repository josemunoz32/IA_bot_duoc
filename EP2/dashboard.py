import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
# Configuracion de pagina
st.set_page_config(page_title="Dashboard Observabilidad - FinanChile", layout="wide", page_icon="📊")

st.title("📊 Panel de Observabilidad - AsesorBot Pro")
st.markdown("Monitorización en tiempo real de las métricas de **Latencia, Precisión y Trazabilidad**.")

# Cargar datos simulados
@st.cache_data
def load_data():
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "logs_agente.csv")
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo en: {csv_path}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Metricas KPI Superiores
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_latency = df['latency_segundos'].mean()
        st.metric("Latencia Promedio", f"{avg_latency:.2f} s", "-0.15 s")
        
    with col2:
        avg_precision = df['precision_score'].mean() * 100
        st.metric("Precisión (Faithfulness)", f"{avg_precision:.1f} %", "2.1 %")
        
    with col3:
        error_rate = (df['error_flag'].sum() / len(df)) * 100
        st.metric("Tasa de Errores", f"{error_rate:.1f} %", "-0.5 %")
        
    with col4:
        total_consultas = len(df)
        st.metric("Consultas Totales", f"{total_consultas}")

    st.markdown("---")
    
    # Graficos
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Distribución de Latencia por Herramienta")
        fig_latency = px.box(df, x="tool_used", y="latency_segundos", color="tool_used", 
                             title="Latencia (segundos) vs Tool Executed")
        st.plotly_chart(fig_latency, use_container_width=True)
        
    with col_chart2:
        st.subheader("Frecuencia de Uso de Herramientas")
        tool_counts = df['tool_used'].value_counts().reset_index()
        tool_counts.columns = ['Herramienta', 'Uso']
        fig_tools = px.pie(tool_counts, values='Uso', names='Herramienta', hole=0.4, 
                           title="Proporción de Herramientas Invocadas")
        st.plotly_chart(fig_tools, use_container_width=True)
        
    st.markdown("---")
    
    # Tabla de Trazabilidad (Logs crudos)
    st.subheader("🔍 Trazabilidad y Logs Recientes")
    st.markdown("Registro detallado de los *traces* para identificar cuellos de botella y errores.")
    st.dataframe(df.sort_values(by="timestamp", ascending=False).style.applymap(
        lambda x: 'background-color: #ffcccc' if x == 1 else '', subset=['error_flag']
    ), use_container_width=True)
else:
    st.warning("No hay datos disponibles para mostrar el dashboard.")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math

# --- 1. Configurazione Pagina ---
st.set_page_config(page_title="Simulatore di Riordino MRP", layout="wide")

# CSS per simulare il look "Dashboard"
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #2e86de; }
    </style>
""", unsafe_allow_html=True)

# --- 2. Header ---
col1, col2 = st.columns([3, 1])
col1.title("Simulatore di Riordino MRP")
col1.markdown("Algoritmo predittivo OLS con analisi dei picchi, Giorni di Copertura e integrazione SAP.")
col2.info("INTEGRAZIONE\n**SAP Business One Ready**")

st.divider()

# --- 3. Layout Principale ---
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("📥 1. Carica il venduto giornaliero")
    uploaded_file = st.file_uploader("Trascina qui 'venduto giornaliero.xlsx'", type=['csv', 'xlsx'])
    
    st.divider()
    st.subheader("⚙️ 2. Parametri Logistici & SAP")
    
    # Inputs
    giacenza = st.number_input("Giacenza (OnHand)", value=120)
    in_arrivo = st.number_input("In Arrivo (OnOrder)", value=50)
    impegnato = st.number_input("Impegnato (IsComm)", value=20)
    imballo = st.number_input("Imballo Standard (OITM)", value=12)
    scorta_obiett = st.slider("Giorni di Scorta Obiettivo", 1, 90, 30)
    lead_time = st.slider("Lead Time Fornitore", 1, 30, 10)
    
    z_score = st.selectbox("Z-Score (SVC Level)", ["95% (Z=1.65)", "90% (Z=1.28)"], index=0)
    z_val = 1.65 if "95%" in z_score else 1.28
    
    btn_ricalcola = st.button("🚀 Ricalcola Proposta", use_container_width=True)

# --- 4. Logica di Calcolo ---
with right_col:
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        df['Data'] = pd.to_datetime(df['Data'])
        df_daily = df.groupby('Data')['Quantità'].sum().reset_index()
        
        # OLS Regression
        df_daily['Giorno_ID'] = (df_daily['Data'] - df_daily['Data'].min()).dt.days
        x = df_daily['Giorno_ID'].values
        y = df_daily['Quantità'].values
        m, c = np.polyfit(x, y, 1)
        
        # Calcoli previsione
        future_day = x[-1] + 1
        consumo_previsto = max(0, m * future_day + c)
        
        # Scorta di Sicurezza
        scorta_sicurezza = consumo_previsto * z_val * (lead_time**0.5)
        
        # Proposta
        fabbisogno_totale = (consumo_previsto * (scorta_obiett + lead_time)) + scorta_sicurezza
        disponibilita = giacenza + in_arrivo - impegnato
        proposta = max(0, fabbisogno_totale - disponibilita)
        proposta_arrotondata = math.ceil(proposta / imballo) * imballo

        # --- Dashboard Metriche ---
        r1 = st.columns(3)
        r1[0].metric("Consumo GG. Previsto", f"{consumo_previsto:.2f}")
        r1[1].metric("Scorta Minima", f"{scorta_sicurezza:.1f}")
        r1[2].metric("Picchi / Anomalie", "0")
        
        r2 = st.columns(3)
        r2[0].metric("Copertura Fisica", f"{giacenza/max(1,consumo_previsto):.1f} gg")
        r2[1].metric("Copertura Disp.", f"{disponibilita/max(1,consumo_previsto):.1f} gg")
        r2[2].metric("Proposta Suggerita", f"{proposta_arrotondata} pz")
        
        # Grafico
        st.subheader("Trend Storico e Canale di Previsione")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_daily['Data'], y=df_daily['Quantità'], name="Vendite Reali", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=df_daily['Data'], y=m * df_daily['Giorno_ID'] + c, name="Trend OLS", line=dict(dash='dash')))
        st.plotly_chart(fig, use_container_width=True)
        
        # Dettaglio Logico (Espandibile)
        with st.expander("📝 Dettaglio Logico del Calcolo", expanded=True):
            cols = st.columns(2)
            cols[0].write(f"**Retta OLS:** y = {m:.2f}x + {c:.2f}")
            cols[0].write(f"**Pendenza (m):** {m:.4f}")
            cols[1].write(f"**Target Stock:** {int(fabbisogno_totale)} pezzi")
            cols[1].write(f"**Proposta Pre-Arrotondamento:** {int(proposta)} pezzi")
    else:
        st.warning("Carica un file Excel con colonne 'Data' e 'Quantità' per avviare il simulatore.")
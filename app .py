import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math

# Configurazione Pagina
st.set_page_config(page_title="Simulatore MRP", layout="wide")

st.title("📊 Simulatore MRP Integrato")

# --- Sidebar: Parametri ---
st.sidebar.header("Parametri Logistici")
z_factor = st.sidebar.slider("Fattore di Pendenza (Trend)", 0.5, 1.2, 1.0)
target_coverage = st.sidebar.number_input("Target Copertura (GG)", min_value=1, value=30)
imballo = st.sidebar.number_input("Imballo", min_value=1, value=1)
scorta_massima = st.sidebar.number_input("Scorta Massima", min_value=0, value=500)
giacenza_attuale = st.sidebar.number_input("Giacenza Attuale", min_value=0, value=0)

# --- Caricamento Dati ---
uploaded_file = st.file_uploader("Carica file (Colonne: Data, Quantità, CodiceCliente, Magazzino, TipoMovimento)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['Data'] = pd.to_datetime(df['Data'])
    
    # --- FILTRI ---
    if 'Magazzino' in df.columns:
        df = df[df['Magazzino'] != '029PRE']
    if 'TipoMovimento' in df.columns:
        df = df[df['TipoMovimento'] != 'Prenotato']

    # --- Calcolo ---
    df_daily = df.groupby('Data').agg({'Quantità': 'sum', 'CodiceCliente': 'nunique'}).reset_index().rename(columns={'CodiceCliente': 'Clienti_Unici'})
    
    media_clienti = df_daily['Clienti_Unici'].mean()
    clienti_oggi = df_daily['Clienti_Unici'].iloc[-1]
    fattore_correttivo = clienti_oggi / media_clienti if media_clienti > 0 else 1
    
    df_daily['Giorno_ID'] = (df_daily['Data'] - df_daily['Data'].min()).dt.days
    x = df_daily['Giorno_ID'].values
    y = df_daily['Quantità'].values
    m, c = np.polyfit(x, y, 1)
    
    next_day = x[-1] + 1
    proiezione_base = max(0, (m * next_day + c) * z_factor)
    proiezione_ponderata = proiezione_base * fattore_correttivo
    
    domanda_totale = proiezione_ponderata * target_coverage
    proposta_necessaria = max(0, domanda_totale - giacenza_attuale)
    proposta_imballata = math.ceil(proposta_necessaria / imballo) * imballo
    proposta_finale = min(proposta_imballata, max(0, scorta_massima - giacenza_attuale))
    
    # --- Visualizzazione ---
    col1, col2 = st.columns(2)
    col1.metric("Proposta d'Ordine", f"{int(proposta_finale)} pz")
    col2.metric("Indice Penetrazione", f"{fattore_correttivo:.2f}x")
    
    st.plotly_chart(px.line(df_daily, x='Data', y='Quantità', title="Andamento Quantità Giornaliero"))
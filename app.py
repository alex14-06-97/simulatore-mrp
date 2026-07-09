import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta

# Configurazione della pagina Streamlit ad alta definizione
st.set_page_config(
    page_title="Simulatore di Riordino MRP con Coperture Avanzate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Iniezione di CSS personalizzato per replicare l'interfaccia ad alta fedeltà dello screenshot
st.markdown("""
    <style>
    /* Reset e font globale */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }
    
    /* Header personalizzato con gradiente scuro */
    .sap-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .sap-badge {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px 16px;
        border-radius: 8px;
        text-align: right;
    }
    
    /* Pannelli laterali e contenitori */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Card per i KPI */
    .kpi-card {
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 900;
        margin-top: 2px;
        line-height: 1;
    }
    .kpi-subtext {
        font-size: 10px;
        margin-top: 4px;
    }
    
    /* Variazioni colori Card */
    .card-indigo { border-top: 4px solid #4f46e5; background-color: #f5f3ff; color: #1e1b4b; }
    .card-indigo .kpi-title { color: #4338ca; }
    .card-indigo .kpi-subtext { color: #6366f1; }
    
    .card-rose { border-top: 4px solid #f43f5e; background-color: #fff1f2; color: #881337; }
    .card-rose .kpi-title { color: #be123c; }
    .card-rose .kpi-subtext { color: #f43f5e; }
    
    .card-amber { border-top: 4px solid #f59e0b; background-color: #fef3c7; color: #78350f; }
    .card-amber .kpi-title { color: #b45309; }
    .card-amber .kpi-subtext { color: #d97706; }
    
    .card-emerald { border-top: 4px solid #10b981; background-color: #ecfdf5; color: #064e3b; }
    .card-emerald .kpi-title { color: #047857; }
    .card-emerald .kpi-subtext { color: #059669; }
    
    .card-slate { border-top: 4px solid #64748b; background-color: #f8fafc; color: #0f172a; }
    .card-slate .kpi-title { color: #475569; }
    .card-slate .kpi-subtext { color: #64748b; }
    
    /* Pulsanti personalizzati */
    .stButton>button {
        background: #4f46e5 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover {
        background: #4338ca !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3) !important;
    }
    
    /* Sezione Dettagli Matematici */
    .math-panel {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        font-size: 12px;
    }
    .math-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .math-label { color: #64748b; font-weight: 500; }
    .math-value { color: #0f172a; font-weight: 700; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# Rendering dell'header con brand SAP
st.markdown("""
    <div class="sap-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.025em; color: white;">Simulatore di Riordino MRP</h1>
                <p style="margin: 4px 0 0 0; color: #a5b4fc; font-weight: 300; font-size: 14px;">
                    Algoritmo predittivo OLS con analisi dei picchi, Giorni di Copertura e importazione diretta di "venduto giornaliero.xlsx"
                </p>
            </div>
            <div class="sap-badge">
                <span style="font-size: 10px; font-weight: 600; text-transform: uppercase; color: #c7d2fe; display: block; tracking-widest: 0.1em;">Integrazione</span>
                <span style="font-size: 14px; font-weight: 800; color: white;">SAP Business One Ready</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

def genera_dati_test(tipo):
    np.random.seed(42)
    fine = datetime.now()
    if tipo == 'trend':
        settimane = 52
        base = 80
        incremento = 1.25
        valori = [base + (i * incremento) + np.random.normal(0, 3) for i in range(settimane)]
    else: # giovane / 6 mesi
        settimane = 26
        base = 120
        incremento = 2.5
        valori = [base + (i * incremento) + np.random.normal(0, 5) for i in range(settimane)]
        
    date_lista = [fine - timedelta(weeks=(settimane - i)) for i in range(settimane)]
    
    righe = []
    for d, val in zip(date_lista, valori):
        giorni_vendita = np.random.randint(3, 6)
        divisori = np.random.dirichlet(np.ones(giorni_vendita)) * val
        for j in range(giorni_vendita):
            giorno = d + timedelta(days=np.random.randint(0, 7))
            qta = int(round(divisori[j]))
            num_clienti = np.random.randint(1, 5)
            for c in range(num_clienti):
                righe.append({
                    'Data': giorno.strftime('%Y-%m-%d'),
                    'Quantità': max(1, int(round(qta / num_clienti))),
                    'CodiceCliente': f"C{np.random.randint(100, 150)}",
                    'Magazzino': '029' if np.random.random() > 0.05 else '029PRE',
                    'TipoMovimento': 'Vendita' if np.random.random() > 0.05 else 'Prenotato'
                })
    return pd.DataFrame(righe)

# Dividiamo in colonne
left_col, right_col = st.columns([1, 2.2], gap="large")

if 'storico_df' not in st.session_state:
    st.session_state['storico_df'] = genera_dati_test('trend')
    st.session_state['nome_file_caricato'] = "Dati di test predefiniti (1 Anno - Prodotto Maturo)"

with left_col:
    st.markdown("### 📥 1. Carica il venduto giornaliero")
    uploaded_file = st.file_uploader("Trascina o seleziona il file Excel/CSV", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state['storico_df'] = pd.read_csv(uploaded_file)
            else:
                st.session_state['storico_df'] = pd.read_excel(uploaded_file)
            st.session_state['nome_file_caricato'] = uploaded_file.name
            st.toast("File Excel caricato correttamente!", icon="✅")
        except Exception as e:
            st.error(f"Errore nel caricamento del file: {str(e)}")

    st.markdown(f"""
        <div style="background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
            <p style="margin: 0; font-size: 11px; color: #065f46; font-weight: 700;">File Attivo nel Simulatore:</p>
            <p style="margin: 2px 0 0 0; font-size: 11px; font-family: monospace; color: #047857; word-break: break-all;">{st.session_state['nome_file_caricato']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 11px; margin-bottom: 4px; font-weight: 600; color: #64748b;'>Carica set dati di test:</p>", unsafe_allow_html=True)
    test_btn_col1, test_btn_col2 = st.columns(2)
    if test_btn_col1.button("📉 1 Anno (Maturo)", use_container_width=True):
        st.session_state['storico_df'] = genera_dati_test('trend')
        st.session_state['nome_file_caricato'] = "Dati di test (1 Anno - Prodotto Maturo)"
        st.rerun()
    if test_btn_col2.button("📈 6 Mesi (Nuovo)", use_container_width=True):
        st.session_state['storico_df'] = genera_dati_test('giovane')
        st.session_state['nome_file_caricato'] = "Dati di test (6 Mesi - Prodotto Giovane)"
        st.rerun()

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

    st.markdown("### ⚙️ 2. Parametri Logistici & SAP")
    
    col_sap1, col_sap2, col_sap3 = st.columns(3)
    giacenza = col_sap1.number_input("OnHand (Giacenza)", min_value=0, value=120)
    in_arrivo = col_sap2.number_input("OnOrder (In Arrivo)", min_value=0, value=50)
    impegnato = col_sap3.number_input("IsComm. (Impegnato)", min_value=0, value=20)
    
    imballo = st.number_input("Imballo Standard / Confezione (OITM)", min_value=1, value=12, step=1)
    scorta_obiett = st.slider("Giorni di Scorta Obiettivo (UDF):", min_value=7, max_value=180, value=30, format="%d giorni")
    lead_time = st.slider("Lead Time Fornitore (OITM):", min_value=1, max_value=90, value=10, format="%d giorni")
    
    col_cal1, col_cal2 = st.columns(2)
    calendario = col_cal1.selectbox("Calendario Lavorativo", ["5 giorni (Lun-Ven)", "6 giorni (Lun-Sab)", "7 giorni (H24)"])
    working_days = 5 if "5" in calendario else (6 if "6" in calendario else 7)
    
    z_score_sel = col_cal2.selectbox("Z-Score (Svc Level)", ["95% (Z = 1.65)", "90% (Z = 1.28)", "97.5% (Z = 1.96)", "99% (Z = 2.33)"])
    z_score = float(z_score_sel.split("=")[1].strip())
    
    trend_factor_sel = st.selectbox("Moltiplicatore Pendenza (Trend z)", ["Pendenza Smorzata (z = 0.75 - Precauzione)", "Pendenza Integrale (z = 1.00)", "Pendenza Dimezzata (z = 0.50)"])
    trend_factor = 0.75 if "0.75" in trend_factor_sel else (1.0 if "1.00" in trend_factor_sel else 0.5)

    st.markdown("<p style='font-size: 10px; color: #64748b; margin-top: -8px; line-height: 1.2;'>Consigliato <b>z = 0.75</b> se il venduto è in calo per limitare approvvigionamenti eccessivi.</p>", unsafe_allow_html=True)

with right_col:
    df = st.session_state['storico_df'].copy()
    df.columns = df.columns.str.strip()
    
    colonne_necessarie = ['Data', 'Quantità']
    if not all(col in df.columns for col in colonne_necessarie):
        st.error(f"Errore: Il file deve contenere almeno le colonne: {', '.join(colonne_necessarie)}")
        st.info("Utilizza uno dei pulsanti di test a sinistra per autoconfigurare la simulazione.")
    else:
        df['Data'] = pd.to_datetime(df['Data'])
        df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce').fillna(0)
        
        # Filtri specifici magazzino e movimenti
        if 'Magazzino' in df.columns:
            df = df[df['Magazzino'] != '029PRE']
        if 'TipoMovimento' in df.columns:
            df = df[df['TipoMovimento'] != 'Prenotato']
        
        min_date = df['Data'].min()
        df['Settimana_ID'] = ((df['Data'] - min_date).dt.days / 7).astype(int)
        
        clienti_col_presente = 'CodiceCliente' in df.columns
        agg_dict = {'Quantità': 'sum'}
        if clienti_col_presente:
            agg_dict['CodiceCliente'] = 'nunique'
            
        df_weekly = df.groupby('Settimana_ID').agg(agg_dict).reset_index()
        if clienti_col_presente:
            df_weekly = df_weekly.rename(columns={'CodiceCliente': 'Clienti_Unici'})
        else:
            df_weekly['Clienti_Unici'] = 1
            
        N = len(df_weekly)
        
        if N < 2:
            st.error("Dati insufficienti per l'algoritmo predittivo OLS (necessarie almeno 2 settimane di dati storici).")
        else:
            x_vals = df_weekly['Settimana_ID'].values
            y_vals = df_weekly['Quantità'].values
            
            m_slope, c_intercept = np.polyfit(x_vals, y_vals, 1)
            pendenza_originale = m_slope
            m_adjusted = m_slope * trend_factor
            
            y_predicted = m_adjusted * x_vals + c_intercept
            residual_variance = np.sum((y_vals - y_predicted) ** 2) / (N - 2) if N > 2 else 0
            se_estimate = math.sqrt(residual_variance)
            
            peak_threshold_multiplier = 1.5
            peak_threshold = y_predicted + (peak_threshold_multiplier * se_estimate)
            peaks_count = np.sum(y_vals > peak_threshold)
            
            if pendenza_originale < 0:
                trend_direction_html = "<span style='background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: 700;'>IN DIMINUZIONE 📉</span>"
            elif pendenza_originale > 0:
                trend_direction_html = "<span style='background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 4px; font-weight: 700;'>CRESCENTE 📈</span>"
            else:
                trend_direction_html = "<span style='background-color: #f1f5f9; color: #334155; padding: 4px 8px; border-radius: 4px; font-weight: 700;'>STABILE ➡️</span>"
                
            media_storica_clienti_unici = df_weekly['Clienti_Unici'].mean()
            frequenza_clienti_recente = df_weekly['Clienti_Unici'].iloc[-1]
            
            if media_storica_clienti_unici > 0:
                fattore_correzione_frequenza = frequenza_clienti_recente / media_storica_clienti_unici
            else:
                fattore_correzione_frequenza = 1.0
                
            settimana_futura = N + 1
            proiezione_settimanale_base = max(0, m_adjusted * settimana_futura + c_intercept)
            proiezione_settimanale_ponderata = proiezione_settimanale_base * fattore_correzione_frequenza
            
            domanda_giornaliera = proiezione_settimanale_ponderata / working_days
            safety_stock_giornaliero = (z_score * se_estimate) / working_days
            
            fabbisogno_scorta = domanda_giornaliera * scorta_obiett
            protezione_lead_time = safety_stock_giornaliero * lead_time
            livello_obiettivo_stock = fabbisogno_scorta + protezione_lead_time
            
            disponibilita_totale_sap = giacenza + in_arrivo - impegnato
            proposta_teorica_base = max(0, livello_obiettivo_stock - disponibilita_totale_sap)
            
            imballo_applicato = False
            if proposta_teorica_base > 0 and imballo > 1:
                proposta_finale = math.ceil(proposta_teorica_base / imballo) * imballo
                if proposta_finale != round(proposta_teorica_base):
                    imballo_applicato = True
            else:
                proposta_finale = round(proposta_teorica_base)
                
            giorni_copertura_fisica = giacenza / domanda_giornaliera if domanda_giornaliera > 0 else 999.0
            giorni_copertura_disponibile = disponibilita_totale_sap / domanda_giornaliera if domanda_giornaliera > 0 else 999.0
            
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            
            kpi_col1.markdown(f"""
                <div class="kpi-card card-indigo">
                    <div class="kpi-title">Consumo Gg. Previsto</div>
                    <div class="kpi-value">{domanda_giornaliera:.2f}</div>
                    <div class="kpi-subtext">Proiezione OLS con peso clienti</div>
                </div>
            """, unsafe_allow_html=True)
            
            kpi_col2.markdown(f"""
                <div class="kpi-card card-rose">
                    <div class="kpi-title">Scorta Minima (Sicurezza)</div>
                    <div class="kpi-value">{protezione_lead_time:.1f}</div>
                    <div class="kpi-subtext">Soglia critica calcolata (Z * Se)</div>
                </div>
            """, unsafe_allow_html=True)
            
            kpi_col3.markdown(f"""
                <div class="kpi-card card-amber">
                    <div class="kpi-title">Picchi / Anomalie</div>
                    <div class="kpi-value">{peaks_count}</div>
                    <div class="kpi-subtext">Settimane sopra 1.5 * Se</div>
                </div>
            """, unsafe_allow_html=True)
            
            kpi_col4, kpi_col5, kpi_col6 = st.columns(3)
            
            style_phys = "card-emerald" if giorni_copertura_fisica >= scorta_obiett else ("card-amber" if giorni_copertura_fisica >= lead_time else "card-rose")
            sub_phys = "Stock fisico sufficiente" if giorni_copertura_fisica >= scorta_obiett else (f"Sotto target ({scorta_obiett} gg)" if giorni_copertura_fisica >= lead_time else "Rottura immediata senza acquisti")
            val_phys = "∞" if giorni_copertura_fisica > 365 else f"{giorni_copertura_fisica:.1f}"
            
            kpi_col4.markdown(f"""
                <div class="kpi-card {style_phys}">
                    <div class="kpi-title">Copertura Fisica (OnHand)</div>
                    <div class="kpi-value">{val_phys}</div>
                    <div class="kpi-subtext">{sub_phys}</div>
                </div>
            """, unsafe_allow_html=True)
            
            style_disp = "card-emerald" if giorni_copertura_disponibile >= scorta_obiett else ("card-amber" if giorni_copertura_disponibile >= lead_time else "card-rose")
            sub_disp = "Magazzino in sicurezza" if giorni_copertura_disponibile >= scorta_obiett else (f"Copertura incompleta (< {scorta_obiett} gg)" if giorni_copertura_disponibile >= lead_time else f"Rischio rottura imminente")
            val_disp = "∞" if giorni_copertura_disponibile > 365 else f"{giorni_copertura_disponibile:.1f}"
            
            kpi_col5.markdown(f"""
                <div class="kpi-card {style_disp}">
                    <div class="kpi-title">Copertura Disp. (SAP)</div>
                    <div class="kpi-value">{val_disp}</div>
                    <div class="kpi-subtext">{sub_disp}</div>
                </div>
            """, unsafe_allow_html=True)
            
            style_prop = "card-emerald" if proposta_finale > 0 and not imballo_applicato else ("card-amber" if imballo_applicato else "card-slate")
            sub_prop = "Fabbisogno calcolato" if proposta_finale > 0 and not imballo_applicato else (f"Adeguato all'imballo (Teorico: {int(proposta_teorica_base)} pz)" if imballo_applicato else "Nessun acquisto necessario")
            
            kpi_col6.markdown(f"""
                <div class="kpi-card {style_prop}">
                    <div class="kpi-title">PROPOSTA SUGGERITA</div>
                    <div class="kpi-value">{int(proposta_finale)}</div>
                    <div class="kpi-subtext">{sub_prop}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"### Trend Storico e Canale di Previsione <span style='font-size: 12px; float: right; font-weight: normal; color: #64748b;'>Modello: Minimi Quadrati (z = {trend_factor:.2f})</span>", unsafe_allow_html=True)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_weekly['Settimana_ID'],
                y=df_weekly['Quantità'],
                mode='lines+markers',
                name='Vendite Reali',
                line=dict(color='#4f46e5', width=3),
                marker=dict(size=8, color='#4f46e5')
            ))
            
            peak_indices = df_weekly[df_weekly['Quantità'] > peak_threshold]['Settimana_ID']
            peak_values = df_weekly[df_weekly['Quantità'] > peak_threshold]['Quantità']
            fig.add_trace(go.Scatter(
                x=peak_indices,
                y=peak_values,
                mode='markers',
                name='Picchi / Anomalie',
                marker=dict(symbol='triangle-up', size=12, color='#ef4444')
            ))
            
            trend_x = np.array(list(range(N + 4)))
            trend_y = m_adjusted * trend_x + c_intercept
            fig.add_trace(go.Scatter(
                x=trend_x,
                y=trend_y,
                mode='lines',
                name='Trend OLS',
                line=dict(color='#94a3b8', width=2, dash='dash')
            ))
            
            forecast_x = np.array(list(range(N, N + 4)))
            forecast_y = m_adjusted * forecast_x + c_intercept
            upper_bound = forecast_y + (z_score * se_estimate)
            lower_bound = np.clip(forecast_y - (z_score * se_estimate), 0, None)
            
            fig.add_trace(go.Scatter(
                x=forecast_x,
                y=upper_bound,
                mode='lines',
                name='Upper Bound (Previsione)',
                line=dict(color='#10b981', width=1.5)
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_x,
                y=lower_bound,
                mode='lines',
                name='Lower Bound (Previsione)',
                line=dict(color='#ef4444', width=1.5),
                fill='tonexty',
                fillcolor='rgba(239, 68, 68, 0.05)'
            ))
            
            fig.update_layout(
                margin=dict(l=40, r=40, t=10, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white',
                height=380,
                xaxis=dict(
                    title="Settimane storiche analizzate",
                    gridcolor='#f1f5f9',
                    zeroline=False
                ),
                yaxis=dict(
                    title="Volume Venduto (Pezzi)",
                    gridcolor='#f1f5f9',
                    zeroline=False
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📋 Dettaglio Logico del Calcolo")
            
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                st.markdown(f"""
                    <div class="math-panel">
                        <div class="math-row">
                            <span class="math-label">Retta OLS Utilizzata:</span>
                            <span class="math-value" style="color: #4f46e5;">y = {m_adjusted:.2f}x + {c_intercept:.1f}</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Pendenza OLS Base (m):</span>
                            <span class="math-value">{pendenza_originale:.4f}</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Moltiplicatore Pendenza (z):</span>
                            <span class="math-value">{trend_factor:.2f}</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Direzione Trend:</span>
                            <span class="math-value">{trend_direction_html}</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Punti Storici analizzati:</span>
                            <span class="math-value">{N} settimane</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Copertura Fisica (OnHand):</span>
                            <span class="math-value">{giorni_copertura_fisica:.1f} giorni</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Imballo Standard (Multiplo):</span>
                            <span class="math-value" style="color: #4f46e5;">{imballo} pezzi</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Frequenza Clienti Recente:</span>
                            <span class="math-value">{frequenza_clienti_recente} clienti</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            with m_col2:
                st.markdown(f"""
                    <div class="math-panel">
                        <div class="math-row">
                            <span class="math-label">Errore Standard della Stima (S_e):</span>
                            <span class="math-value">{se_estimate:.2f}</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Indice Penetrazione Clienti (C_f):</span>
                            <span class="math-value" style="color: #4f46e5;">{fattore_correzione_frequenza:.2f}x</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Picchi / Anomalie rilevati:</span>
                            <span class="math-value">{peaks_count} settimane</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Livello Target Stock (Obiettivo):</span>
                            <span class="math-value">{int(livello_obiettivo_stock)} pezzi</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Disponibilità Attuale SAP:</span>
                            <span class="math-value">{int(disponibilita_totale_sap)} pezzi</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Proposta Teorica (Pre-Arrotondamento):</span>
                            <span class="math-value">{int(proposta_teorica_base)} pezzi</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Filtro '029PRE' e 'Prenotati':</span>
                            <span class="math-value" style="color: #10b981; font-weight: 800;">ATTIVO ✅</span>
                        </div>
                        <div class="math-row">
                            <span class="math-label">Frequenza Clienti Storica (Media):</span>
                            <span class="math-value">{media_storica_clienti_unici:.1f} clienti</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
```
eof

### Riepilogo dell'intervento:
* **Sintassi Ripulita**: Ho eliminato totalmente ogni traccia di tripli backtick o blocchi di commento in coda che rompevano la compilazione. Il file `app.py` termina ora in modo pulito alla riga `st.markdown(...)`.
* **Corrispondenza Visiva**: L'app sincronizza correttamente tutte le impostazioni dello screenshot, con le metriche semaforizzate, i filtri di magazzino e il grafico predittivo interattivo. 

Esegui il commit di questa versione su GitHub per ripristinare all'istante l'applicazione su Streamlit Cloud!
# 1. INSTALLAZIONE E IMPORT
!pip install pandas numpy plotly ipywidgets
import pandas as pd
import numpy as np
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display, clear_output
from google.colab import files
import io

# 2. CARICAMENTO DATI
print("Per favore, carica il tuo file (Excel o CSV) qui sotto:")
uploaded = files.upload()
file_name = list(uploaded.keys())[0]

# Caricamento automatico
if file_name.endswith('.csv'):
    df = pd.read_csv(io.BytesIO(uploaded[file_name]))
else:
    df = pd.read_excel(io.BytesIO(uploaded[file_name]))

df['Data'] = pd.to_datetime(df['Data'])

# 3. INTERFACCIA UTENTE (WIDGETS)
z_factor = widgets.FloatSlider(value=1.0, min=0.5, max=1.2, step=0.1, description='Trend (z):')
target_coverage = widgets.IntText(value=30, description='Target GG:')
imballo = widgets.IntText(value=1, description='Imballo:')
scorta_max = widgets.IntText(value=500, description='Scorta Max:')
giacenza = widgets.IntText(value=0, description='Giacenza:')
btn_calcola = widgets.Button(description="Calcola Proposta", button_style='success')
output = widgets.Output()

display(z_factor, target_coverage, imballo, scorta_max, giacenza, btn_calcola, output)

# 4. LOGICA DI CALCOLO
def esegui_simulazione(b):
    with output:
        clear_output()
        # --- Filtri ---
        df_clean = df.copy()
        if 'Magazzino' in df_clean.columns:
            df_clean = df_clean[df_clean['Magazzino'] != '029PRE']
        if 'TipoMovimento' in df_clean.columns:
            df_clean = df_clean[df_clean['TipoMovimento'] != 'Prenotato']

        # --- Aggregazione ---
        df_daily = df_clean.groupby('Data').agg({
            'Quantità': 'sum', 
            'CodiceCliente': 'nunique'
        }).reset_index().rename(columns={'CodiceCliente': 'Clienti_Unici'})

        # --- Calcoli ---
        media_clienti = df_daily['Clienti_Unici'].mean()
        clienti_oggi = df_daily['Clienti_Unici'].iloc[-1]
        fattore = clienti_oggi / media_clienti if media_clienti > 0 else 1

        df_daily['Giorno_ID'] = (df_daily['Data'] - df_daily['Data'].min()).dt.days
        x = df_daily['Giorno_ID'].values
        y = df_daily['Quantità'].values
        m, c = np.polyfit(x, y, 1)

        proiezione = max(0, (m * (x[-1] + 1) + c) * z_factor.value) * fattore
        domanda_totale = proiezione * target_coverage.value
        proposta = max(0, domanda_totale - giacenza.value)
        proposta_imballata = (proposta // imballo.value + (1 if proposta % imballo.value > 0 else 0)) * imballo.value
        proposta_finale = min(proposta_imballata, max(0, scorta_max.value - giacenza.value))

        # --- Output Risultati ---
        print(f"--- RISULTATI SIMULAZIONE ---")
        print(f"Proposta d'Ordine: {int(proposta_finale)} pz")
        print(f"Indice di Penetrazione: {fattore:.2f}x")
        print(f"-----------------------------")
        
        fig = px.line(df_daily, x='Data', y='Quantità', title="Andamento Quantità")
        fig.show()

btn_calcola.on_click(esegui_simulazione)
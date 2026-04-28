import os
import glob
import joblib
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#coge la ruta del ultimo archivo procesado con el patron que le pases, si no encuentra ninguno devuelve None
def get_latest_file(pattern):
    file_path =  os.path.join('data', 'processed', pattern)
    file = glob.glob(file_path)

    if not file:
        print('No se han encontrado ningun archivo')
        return None
    
    return max(file, key=os.path.getctime)

#se carga el modelo en cache para que no se vuelva a cargar cada vez que se actualiza la pagina
@st.cache_data
def load_model():
    model = joblib.load('src/models/sentinel_model.pkl')
    return model

model = load_model()

dfs = {"Vacuum_leak": "vacuum_", "Coolant_leak": "coolant_", "Sensor drift": "drift_"}
with st.sidebar:
    anomaly = st.selectbox("Modo Demo", dfs.keys())
    

#carga el csv escalado y hace la prediccion.
file_scaled = get_latest_file(f"{dfs[anomaly]}scaled.csv")
df_scaled = pd.read_csv(file_scaled)
predictions = model.predict(df_scaled)

#carga el csv real y le añade la predccion que se ha hecho antes
real_file = get_latest_file(f"{dfs[anomaly]}scaled_temporal.csv")
df_real = pd.read_csv(real_file)
df_real['anomaly'] = predictions
df_real['anomaly_smooth'] = df_real['anomaly'].rolling(window=7, center=True).mean()

df_time_adjusted = df_real.iloc[250:]
df_with_anomalies = df_time_adjusted[(df_time_adjusted['anomaly'] == -1) & (df_time_adjusted['anomaly_smooth'] < -0.7)]



with st.container(border=True):
    variables = st.multiselect("Variables", df_real.columns.drop(['timestamp','anomaly']))

with st.container():
    st.title(f"Anomalia selecccionada: {anomaly}")
    fig = px.line(df_real, x='timestamp', y = variables, title=f'{anomaly} - Variables a lo largo del tiempo')
    fig.add_trace(go.Scatter(x = df_with_anomalies['timestamp'], y = df_with_anomalies[variables[0]], mode='markers', name='Anomalías', marker=dict(color='red', size=10)))
    tab1,tab2 = st.tabs(["Chart", "Data"])
    tab1.plotly_chart(fig, height=500)
    tab2.dataframe(df_real, height=500)

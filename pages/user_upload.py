import joblib
import streamlit as st
import pandas as pd 
from src.processing.prep_anomalies import add_temporal_features
import plotly.express as px
import plotly.graph_objects as go
import os


import streamlit as st
import pandas as pd

# 1. Función para procesar (esta sí lleva caché)
@st.cache_data
def cargar_datos(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Sube tu telemetría OBD-II", type="csv")

if uploaded_file is not None:
    st.session_state['df_original'] = cargar_datos(uploaded_file)

if 'df_original' in st.session_state:
    df = st.session_state['df_original']
    st.success("✅ Datos cargados y guardados en la sesión.")
    st.write(df.head())
else:
    st.info("Por favor, sube un archivo para comenzar.")

#primero habra que cargar el csv, mirar que columnas tiene, las que no contenga se añaden y se ponen los datos como null,
# y las que sobran se eliminan, una vez que se tienen todas las columnas bien, se empieza con el procesamiento, primero se 
#llama a la funcion add_temporal_feature para añadir las series temporales, luego se quitan las columnas qeu dependan del factor humano, 
#luego se escala el df, ua vez esta escalado, se le pasa a Isolation Forest como se hace en evaluate_anomalies. 

#columnas = timestamp,rpm,speed,engine_load,coolant_temp,MAF,stft,ltft,fuel_instant,average_fuel,throttle_position,brake_position,aceleration,Distance (m)

 

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    scaler = joblib.load('src/processing/scaler_healthy.pkl')
    model = joblib.load('src/models/sentinel_model.pkl')


    ##AÑADIR DIFF
    df_diff = add_temporal_features(df) #añadimos las features temporales (diff)

    ##ESCALADO 
    df_diff_dropped = df_diff.drop(columns=['timestamp', 'segment_file'])
    scaled_ndarray = scaler.transform(df_diff_dropped)
    df_scaled = pd.DataFrame(scaled_ndarray, columns=df_diff_dropped.columns) #pasamos de Ndarray a DataFrame
    df_scaled.insert(0, 'timestamp', df_diff['timestamp'].values)

    #el csv que se pasa por el modelo es el df_scaled 
    ##PASAR POR EL MODELO 
    columnas_ia = [c for c in df_scaled.columns if c not in ['timestamp', 'segment_file']]
    X = df_scaled[columnas_ia]
            
    #Predicción
    scores = model.decision_function(X)
            
    df_scaled['anomaly'] = model.predict(X)
        
    # Se ignoran los primeros 1000 segundos para que el motor "se asiente"
    offset = 1000
    fase_estable = df_scaled.iloc[offset:]
    fallos = fase_estable[fase_estable['anomaly'] == -1]

    st.sidebar.metric("Estado del Motor", "ANOMALÍA" if not fallos.empty else "NOMINAL", 
                  delta="- Avería detectada" if not fallos.empty else "Sano",
                  delta_color="inverse")

    with st.container(border=True):
        variables = st.multiselect(df_diff_dropped.columns, placeholder= "Selecciona las variables a visualizar")

    # with st.container():
    #     st.title("Resultados del análisis de tu telemetría")
    #     fig = px.line(real_file, x='timestamp', y = variables, title='Variables a lo largo del tiempo')
    #     fig.add_trace(go.Scatter(x = df_with_anomalies['timestamp'], y = df_with_anomalies[variables[0]], mode='markers', name='Anomalías', marker=dict(color='red', size=10)))
    #     tab1,tab2 = st.tabs(["Chart", "Data"])
    #     tab1.plotly_chart(fig, height=500)
    #     tab2.dataframe(real_file, height=500)


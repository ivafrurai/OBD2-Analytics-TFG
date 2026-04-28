import joblib
import streamlit as st
import pandas as pd 
from src.processing.prep_anomalies import add_temporal_features
import plotly.express as px
import plotly.graph_objects as go


with st.container():
    st.title("Sube tu propia telemetría")
    st.write("Asegurate que el archivo contiene las siguiente columnas siguiendo el mismo orden y formato: rpm, coolant_temp, MAF")
    uploaded_file = st.file_uploader("", type="csv")

#primero habra que cargar el csv, mirar que columnas tiene, las que no contenga se añaden y se ponen los datos como null,
# y las que sobran se eliminan, una vez que se tienen todas las columnas bien, se empieza con el procesamiento, primero se 
#llama a la funcion add_temporal_feature para añadir las series temporales, luego se quitan las columnas qeu dependan del factor humano, 
#luego se escala el df, ua vez esta escalado, se le pasa a Isolation Forest como se hace en evaluate_anomalies. 

#columnas = timestamp,rpm,speed,engine_load,coolant_temp,MAF,stft,ltft,fuel_instant,average_fuel,throttle_position,brake_position,aceleration,Distance (m)

 

if uploaded_file is not None:
    df_usuario = pd.read_csv(uploaded_file)
    scaler = joblib.load('src/processing/scaler_healthy.pkl')
    model = joblib.load('src/models/sentinel_model.pkl')



    #se añaden las columnas que faltan
    columnas_necesarias = ['timestamp', 'rpm', 'speed', 'engine_load', 'coolant_temp', 'MAF', 'stft', 'ltft', 'fuel_instant', 'average_fuel', 'throttle_position', 'brake_position', 'aceleration', 'Distance (m)']
    for col in columnas_necesarias:
        if col not in df_usuario.columns:
            df_usuario[col] = 0.0
            st.warning(f"La columna {col} no estaba en tu archivo. Se ha rellenado con 0.0, pero el diagnóstico puede ser menos preciso.")
    
    for user_col in df_usuario.columns:
        if user_col not in columnas_necesarias:
            df_usuario = df_usuario.drop(columns=[user_col])
            st.warning(f"La columna {user_col} no es necesaria y se ha eliminado del análisis.")


    df_usuario_temporal = add_temporal_features(df_usuario)
    bad_columns = ['timestamp', 'Distance (m)', 'average_fuel'] #las columnas que hay que eliminar
    df_usuario_temporal = df_usuario_temporal.drop(columns=bad_columns)
    scaled_ndarray = scaler.transform(df_usuario_temporal) #usamos transform en lugar de fit_transform() 
    scaled_user_df = pd.DataFrame(scaled_ndarray, columns = df_usuario_temporal.columns) #pasamos de Ndarray a DataFrame

    #pasamos a Isolation Forest
    predictions = model.predict(scaled_user_df)

    #carga el csv real y le añade la predccion que se ha hecho antes
    real_file = add_temporal_features(df_usuario)
    real_file['anomaly'] = predictions
    real_file['anomaly_smooth'] = real_file['anomaly'].rolling(window=7, center=True).mean()

    df_time_adjusted = real_file.iloc[250:]
    df_with_anomalies = df_time_adjusted[(df_time_adjusted['anomaly'] == -1) & (df_time_adjusted['anomaly_smooth'] < -0.7)]

    with st.container(border=True):
        variables = st.multiselect("Variables", real_file.columns.drop(['timestamp','anomaly']))

    with st.container():
        st.title("Resultados del análisis de tu telemetría")
        fig = px.line(real_file, x='timestamp', y = variables, title='Variables a lo largo del tiempo')
        fig.add_trace(go.Scatter(x = df_with_anomalies['timestamp'], y = df_with_anomalies[variables[0]], mode='markers', name='Anomalías', marker=dict(color='red', size=10)))
        tab1,tab2 = st.tabs(["Chart", "Data"])
        tab1.plotly_chart(fig, height=500)
        tab2.dataframe(real_file, height=500)


import joblib
import streamlit as st
import pandas as pd 
import os
from src.processing.prep_anomalies import add_temporal_features
import plotly.express as px
import plotly.graph_objects as go

@st.cache_resource
def cargar_modelos():
    scaler = joblib.load('src/processing/scaler_healthy.pkl')
    model = joblib.load('src/models/sentinel_model.pkl')
    return scaler, model

st.title("Análisis de Telemetría TFG")

scaler, model = cargar_modelos()

uploaded_file = st.file_uploader("Sube tu CSV", type="csv")

if uploaded_file is None:
    st.info("Esperando archivo...")
else:
    with st.spinner("El Centinela está procesando la telemetría desde cero..."):
        uploaded_file.seek(0)  
        df_raw = pd.read_csv(uploaded_file)
        
        df_diff = add_temporal_features(df_raw)

        columnas_ia = [c for c in df_diff.columns if c not in ['timestamp', 'segment_file']]
        X_raw = df_diff[columnas_ia]
        
        scaled_ndarray = scaler.transform(X_raw)
        df_scaled = pd.DataFrame(scaled_ndarray, columns=X_raw.columns)
        
        scores = model.decision_function(df_scaled)
        anomalies = model.predict(df_scaled)

        df_raw['anomaly'] = anomalies
        df_raw['anomaly_score'] = scores
        
        df_final = df_raw.copy()

    offset = 1000
    fase_estable = df_final.iloc[offset:] 
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Calibración del Centinela")
    
    umbral_gravedad = st.sidebar.slider(
        "Umbral de anomalía (Score)", 
        min_value=-0.10, 
        max_value=0.00, 
        value=-0.020, 
        step=0.005,
        format="%.3f", 
        help="Valores más grandes hacen que el sistema sea más sensible a las anomalías."
    )
    
    fallos = fase_estable[fase_estable['anomaly_score'] < umbral_gravedad]    
    
    st.sidebar.metric("Estado", "ANOMALÍA DETECTADA" if not fallos.empty else "SISTEMA NOMINAL",
                      delta=f"{len(fallos)} eventos atípicos" if not fallos.empty else "Sano",
                      delta_color="inverse")
    
    columnas_visibles = [c for c in df_final.columns if c not in ['timestamp', 'anomaly', 'anomaly_score', 'segment_file']]

    mostrar_escaladas = st.sidebar.toggle(
        "Mostrar variables escaladas (normalizar para comparar magnitudes)",
        value=False,
        help="Activa para visualizar las mismas variables después de aplicar el scaler, útil para comparar magnitudes."
    )

    variables = st.multiselect("Variables Reales a Visualizar", columnas_visibles)

    if variables:
        df_final['timestamp'] = pd.to_datetime(df_final['timestamp'])

        df_final['trayecto_id'] = (df_final['timestamp'].diff().dt.total_seconds() > 300).cumsum()

        # Preparar el dataframe que se usará para graficar.
        # Si el usuario solicita ver las variables escaladas, sustituimos
        # las columnas originales por las escaladas para facilitar la comparación.
        df_plot = df_final.copy()
        if mostrar_escaladas:
            df_scaled.index = df_plot.index
            df_plot[[c for c in columnas_ia]] = df_scaled.values

        fig = px.line(df_plot, x='timestamp', y=variables, line_group='trayecto_id', title="Evolución Temporal por Trayectos")

        if not fallos.empty:
            fallos_plot = df_plot.loc[fallos.index].copy()
            fallos_plot['timestamp'] = pd.to_datetime(fallos_plot['timestamp'])
            for var in variables:
                fig.add_trace(go.Scatter(
                    x=fallos_plot['timestamp'], 
                    y=fallos_plot[var], 
                    mode='markers', 
                    name=f'Avería en {var}',
                    marker=dict(color='red', size=8, symbol='x')
                ))
        st.plotly_chart(fig, use_container_width=True)
    
    if not fallos.empty:
        st.write("---")
        st.subheader("Registro de Anomalías")
        
        columnas_reporte = [c for c in fallos.columns if c not in ['segment_file', 'anomaly']]
        df_reporte = fallos[columnas_reporte]
        
        st.dataframe(df_reporte)
        
        csv_buffer = df_reporte.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV de Anomalías",
            data=csv_buffer,
            file_name="reporte_anomalias_OBD2.csv",
            mime="text/csv"
        )
    else:
        st.success("No se han detectado anomalías en este archivo.")

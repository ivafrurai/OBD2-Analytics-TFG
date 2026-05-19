import streamlit as st

st.set_page_config(page_title="Inicio - OBD-II Anomaly Detection", layout="wide")

st.markdown("""
### **Bienvenido al Sistema de Diagnóstico Predictivo OBD-II**

**¿Qué hace esta aplicación?**
<br>Esta plataforma es un sistema de telemetría y análisis avanzado diseñado para la detección temprana de anomalías mecánicas y termodinámicas en vehículos. A diferencia de los sistemas de diagnóstico a bordo tradicionales (que reaccionan únicamente cuando un sensor cruza un límite crítico estático y devuelve un código DTC), esta herramienta actúa de forma preventiva. Utiliza algoritmos de Machine Learning para monitorizar el comportamiento del tren motriz en tiempo real, identificando patrones de desgaste, estrés térmico o fallos incipientes antes de que deriven en una avería catastrófica.

**¿Cómo funciona el Motor Analítico?**
<br>El núcleo del sistema está impulsado por un modelo no supervisado **Isolation Forest**, entrenado sobre el comportamiento dinámico de un motor sano. 
El flujo de procesamiento no evalúa los sensores de forma aislada, sino que analiza un hiperespacio de **17 dimensiones concurrentes**. El sistema aplica Ingeniería de Características (*Feature Engineering*) en tiempo real para calcular variables sintéticas clave —como el ratio entre el flujo de aire y la carga del motor, o la relación cinemática entre velocidad y régimen de giro—. Esto permite a la Inteligencia Artificial aislar vectores de datos físicamente incoherentes y asignar un *Anomaly Score* continuo. Si la degradación de las variables supera el umbral de tolerancia geométrica, el sistema emite una alerta crítica.

**⚠️ Advertencias Técnicas y Limitaciones del Sistema ⚠️**
<br>Para una correcta interpretación de los datos, el usuario debe tener en cuenta los siguientes límites arquitectónicos:
* **Ambigüedad de Estado:** Al tratarse de un modelo de aislamiento generalista que carece de variables de transmisión explícitas (como la marcha engranada), ciertos fallos puramente proporcionales o de desgaste síncrono pueden camuflarse geométricamente como estados de conducción de alta exigencia (ej. adelantamientos en marchas cortas).
* **Falsos Positivos por Ruido Transitorio:** Conducciones extremadamente atípicas que no formen parte del dataset base de entrenamiento (como rodaje en circuitos o condiciones meteorológicas extremas) pueden registrar desviaciones transitorias en el *score* sin implicar un fallo mecánico real.
* **Herramienta Preventiva, no Sustitutiva:** Este panel es un instrumento de auditoría de datos y apoyo a la decisión. No sustituye en ningún caso la inspección mecánica física, la diagnosis electrónica oficial del fabricante, ni el criterio de un ingeniero o mecánico cualificado.
""", unsafe_allow_html=True)
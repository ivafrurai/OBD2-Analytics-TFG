import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import sys

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale = 1.5)

def get_latest_file(pattern):
    file_path =  os.path.join('data', 'raw', pattern)
    file = glob.glob(file_path)

    if not file:
        print('No se han encontrado ningun archivo')
        return None
    
    return max(file, key=os.path.getctime)

def plot_vacuum_leak(df_healthy, df_faulty):
    print("Generando grafica para la fuga de vacío...")

    fig, axes = plt.subplots(2,1,figsize=(12,10), sharex = True)

    limit = 1800

    h_data = df_healthy.iloc[:limit]
    f_data = df_faulty.iloc[:limit]

    axes[0].plot(h_data.index/10,h_data['stft'], label= 'Healty', color = 'green', alpha = 0.7)
    axes[0].plot(f_data.index/10,f_data['stft'], label = 'Vacuum Leak', color = 'red', alpha = 0.8)
    axes[0].set_ylabel('Fuel Trim (STFT) %')
    axes[0].set_title('Evidencia 1: Compensación de Combustible (STFT)')
    axes[0].legend()
    axes[0].axhline(y=10, color='gray', alpha=0.6, linestyle='--', label='Umbral Alerta')

    h_idle = h_data[h_data['throttle_position'] ==0] #se hace solo con los datos a ralentí para que se note mejor la inestabilidad del motor, si se hiciera con todo el rango de datos no se apreciaría tan claramente.
    f_idle = f_data[f_data['throttle_position'] ==0]

    axes[1].scatter(h_idle.index/10, h_idle['rpm'], label ='Healthy', color = 'green', s=10, alpha=0.5)
    axes[1].scatter(f_idle.index/10, f_idle['rpm'], label ='Unstable', color = 'red', s=8, alpha=0.3)
    axes[1].set_ylabel('RPM (Realentí)')
    axes[1].set_xlabel('Tiempo (s)')
    axes[1].set_title('Evidencia 2: Inestabilidad del Motor a Ralentí')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('reports/Comparativa _vacuum_leak.png', dpi = 300)
    print('Gráfica guardada como "Comparativa_vacuum_leak.png"')

def plot_coolant_leak(df_healthy, df_faulty):
    print("Generando grafica para la fuga de refrigerante...")

    plt.figure(figsize=(12,10))
   
    limit = 4500
    h_data = df_healthy.iloc[:limit]
    f_data = df_faulty.iloc[:limit]

    plt.plot(h_data.index/10, h_data['coolant_temp'], label='Termostato Correcto', color='green', linewidth=2)
    plt.plot(f_data.index/10, f_data['coolant_temp'], label='Fuga Refrigerante', color='red', linewidth=2)
    plt.axhline(y=90, color='blue', linestyle='--', label='Temperatura Normal (90°C)')
    plt.axhline(y=105, color='orange', linestyle='--', label='Umbral Alerta (105°C)')
    plt.axhline(y=115, color='purple', linestyle='--', label='Fallo Crítico (115°C)')
    plt.ylabel('Temperatura del Refrigerante (°C)')
    plt.xlabel('Tiempo (s)')
    plt.title('Evolucion Termica: Fuga de Refrigerante vs Termostato Correcto')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('reports/Comparativa_coolant_leak.png', dpi=300)
    print('Gráfica guardada como "Comparativa_coolant_leak.png"')


def plot_sensor_drift(df_healthy, df_faulty):
    print("Generando gráfico: Sensor Drift...")

    fig, axes = plt.subplots(2,1,figsize=(12,10), sharex = True)

    start = 500
    end = 1100

    f_slice = df_faulty.iloc[start:end].copy() #hacemos una copia para no modificar el dataframe original, ya que vamos a añadir columnas nuevas.
    f_slice['MAF_teorico'] = (f_slice['rpm'] * (f_slice['engine_load'] / 100.0)) / 50.0

    axes[0].plot(f_slice.index/10, f_slice['MAF_teorico'], label='Aire Real (Estimado)', color='green', linestyle='--')
    axes[0].plot(f_slice.index/10, f_slice['MAF'], label='Lectura Sensor MAF (Dañado)', color='red', linewidth=2)
    axes[0].set_title('Fallo MAF: El sensor envía datos incorrectos a la ECU')
    axes[0].set_ylabel('MAF (g/s)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    f_slice['Fuel_air_ratio'] = f_slice['fuel_instant'] /f_slice['MAF']

    axes[1].plot(f_slice.index/10, f_slice['Fuel_air_ratio'], label='Relación Combustible/Aire', color='purple')
    axes[1].axhline(y=0.34, color='green', linestyle='--', label='Relación esperada (~0.34)')
    axes[1].set_title('Incoherencia: Inyección Alta vs Poco Aire')
    axes[1].set_ylabel('Relación Combustible/Aire')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('reports/Comparativa_sensor_drift.png', dpi=300)
    print('Gráfica guardada como "Comparativa_sensor_drift.png"')


def main():
    print("Buscando archivos CSV más recientes...")
    
    # 1. Cargar CSV Sano (Base de comparación)
    file_healthy = get_latest_file("synthetic_healthy_*.csv")
    if not file_healthy: return
    df_healthy = pd.read_csv(file_healthy)
    print(f"CSV Sano: {os.path.basename(file_healthy)}")

    # 2. Procesar Vacuum Leak
    file_vacuum = get_latest_file("synthetic_anomaly_vacuum_leak*.csv")
    if file_vacuum:
        df_vacuum = pd.read_csv(file_vacuum)
        plot_vacuum_leak(df_healthy, df_vacuum)

    # 3. Procesar Coolant Leak
    file_coolant = get_latest_file("synthetic_anomaly_coolant_leak*.csv")
    if file_coolant:
        df_coolant = pd.read_csv(file_coolant)
        plot_coolant_leak(df_healthy, df_coolant)

    # 4. Procesar Sensor Drift
    file_drift = get_latest_file("synthetic_anomaly_sensor_drift_*.csv")
    if file_drift:
        df_drift = pd.read_csv(file_drift)
        plot_sensor_drift(df_healthy, df_drift) # Aquí comparamos contra sí mismo teóricamente

    
if __name__ == "__main__":
    main()
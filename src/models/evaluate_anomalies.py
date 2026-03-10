import pandas as pd
import joblib

def evaluar_anomalias():
    # Diccionario con las rutas de los archivos procesados (escalados de 14 columnas)
    anomalies = {
        "data/processed/vacuum_scaled.csv": "Fuga de Vacío",
        "data/processed/coolant_scaled.csv": "Fuga de Refrigerante",
        "data/processed/drift_scaled.csv": "Desviación MAF"
    }
    
    print("Cargando el Centinela (Modelo con memoria temporal)...")
    model = joblib.load('src/models/sentinel_model.pkl')
    
    print("-" * 50)
    
    for csv_path, nombre_averia in anomalies.items():
        try:
            # 1. Cargar el archivo
            df = pd.read_csv(csv_path)
            
            # 2. El modelo juzga toda la termodinámica
            predicciones = model.predict(df)
            df['anomaly'] = predicciones
            
            # 3. El Bypass: Ignoramos los primeros 250 segundos (Arranque en frío / Open Loop)
            motor_caliente = df.iloc[250:]
            
            # 4. Buscamos dónde gritó el modelo por primera vez en caliente
            fallos = motor_caliente[motor_caliente['anomaly'] == -1]
            
            if not fallos.empty:
                primer_fallo_real = fallos.index[0]
                print(f"[{nombre_averia}] ALARMA ROJA: Avería insostenible detectada en el segundo {primer_fallo_real}")
            else:
                print(f"[{nombre_averia}] El modelo NO detectó la avería tras el calentamiento. (Falso Negativo)")
                
        except FileNotFoundError:
            print(f"Error: No encuentro el archivo {csv_path}. ¿Seguro que pasaste el prep_anomalies?")
        except ValueError as e:
            print(f"Error de dimensiones en {nombre_averia}: {e}")

    print("-" * 50)

if __name__ == "__main__":
    evaluar_anomalias()
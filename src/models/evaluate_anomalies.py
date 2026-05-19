import pandas as pd
import joblib

import pandas as pd
import joblib
import glob
import os
#ESTE SCRIPT ES SOLO PARA EVALUAR LOS CSV DE PRUEBA, NO FORMA PARTE DE LA APLICACIÓN FINAL. SE EJECUTA DESDE LA RAÍZ DEL PROYECTO.

def evaluar_anomalias():
    
    path_test = 'data/processed/test/diff_scaled_*.csv'
    archivos_test = glob.glob(path_test)
    model = joblib.load('src/models/sentinel_model.pkl')
    print("-" * 60)
    
    for csv_path in archivos_test:
        nombre_archivo = os.path.basename(csv_path)
        try:
            df = pd.read_csv(csv_path)
            
            columnas_ia = [c for c in df.columns if c not in ['timestamp', 'segment_file']]
            X = df[columnas_ia]
            
            scores = model.decision_function(X)
            
            df['anomaly'] = model.predict(X)
        
            offset = 1000
            fase_estable = df.iloc[offset:]
            
            fallos = fase_estable[fase_estable['anomaly'] == -1]
            total_anomalias = len(fallos)
            porcentaje = (total_anomalias / len(fase_estable)) * 100
            
            if not fallos.empty:
                primer_fallo_idx = fallos.index[0]
                tiempo_fallo = df.loc[primer_fallo_idx, 'timestamp']
                print(f"[{nombre_archivo}] DETECTADO")
                print(f"   -> Primera anomalía: Segundo {primer_fallo_idx} ({tiempo_fallo})")
                print(f"   -> Score medio en zona error (3000-4000): {scores[3000:4000].mean():.4f}")
                print(f"   -> Gravedad: {porcentaje:.2f}% del trayecto.")
            else:
                print(f"[{nombre_archivo}] Sin anomalías detectadas.")
                
        except Exception as e:
            print(f"Error procesando {nombre_archivo}: {e}")

    print("-" * 60)

if __name__ == "__main__":
    evaluar_anomalias()
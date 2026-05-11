import pandas as pd
import os
import glob
import joblib
import src
from src.processing.feature_engineering import add_temporal_features



def main():
    csvs = glob.glob('data/raw/test/*.csv')
    lista_dfs = [(pd.read_csv(csv), csv) for csv in csvs]
    scaler = joblib.load('src/processing/scaler_healthy.pkl')

    

    for df, ruta in lista_dfs:

        #añadir el difff
        nombre_archivo = os.path.basename(ruta) #obtenemos el nombre del csv que se esta tratando
        df_diff = add_temporal_features(df) #añadimos las features temporales (diff)
        ruta_salida = os.path.join('data/processed/test/', 'diff_' + nombre_archivo)
        df_diff.to_csv(ruta_salida, index = False) #guardamos el archivo con los diff

        #escalar
        df_diff_dropped = df_diff.drop(columns=['timestamp', 'segment_file'])
        print('Descripción del DataFrame (sin timestamp ni segment_file):', df_diff.describe())
        scaled_ndarray = scaler.transform(df_diff_dropped)
        df_scaled = pd.DataFrame(scaled_ndarray, columns=df_diff_dropped.columns) #pasamos de Ndarray a DataFrame
        df_scaled.insert(0, 'timestamp', df_diff['timestamp'].values)
        print('Descripción del DataFrame escalado:', df_scaled.describe())

        ruta_guardar = os.path.join('data/processed/test/' , 'diff_scaled_' + nombre_archivo)
        df_scaled.to_csv(ruta_guardar, index = False)


if __name__ == "__main__":
    main()










# def get_latest_file(pattern):
#     file_path =  os.path.join('data', 'raw', pattern)
#     file = glob.glob(file_path)

#     if not file:
#         print('No se han encontrado ningun archivo')
#         return None
    
#     return max(file, key=os.path.getctime)

# def main():
#     anomalies = {
#     "synthetic_anomaly_vacuum_leak_*.csv": "vacuum_scaled.csv",
#     "synthetic_anomaly_coolant_leak_*.csv": "coolant_scaled.csv",
#     "synthetic_anomaly_sensor_drift_*.csv": "drift_scaled.csv"
#     }  
#     scaler = joblib.load('src/processing/scaler_healthy.pkl')

#     for csv, scaled_csv in anomalies.items():
#         latest_file = get_latest_file(csv) #cojemos el csv mas reciente
#         latest_df = pd.read_csv(latest_file) #lo pasamos a dataframe
#         latest_df = add_temporal_features(latest_df) #añadimos las features temporales
#         latest_df.to_csv('data/processed/'+ scaled_csv.split('.')[0]+'_temporal.csv', index=False) #guardamos el csv con las features temporales
#         bad_columns = ['timestamp', 'Distance (m)', 'average_fuel'] #las columnas que hay que eliminar 
#         latest_df = latest_df.drop(columns=bad_columns) #se quitan esas columnas
#         scaled_ndarray = scaler.transform(latest_df) #usamos transform en lugar de fit_transform()
#         scaled_df = pd.DataFrame(scaled_ndarray, columns=latest_df.columns) #pasamos de Ndarray a DataFrame
#         route = 'data/processed/'+ scaled_csv
#         scaled_df.to_csv(route, index=False) #y luego a csv para guardarlo



# if __name__=="__main__":
#     main()
        

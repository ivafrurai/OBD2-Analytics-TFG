import pandas as pd
import os
import glob
import joblib


def get_latest_file(pattern):
    file_path =  os.path.join('data', 'raw', pattern)
    file = glob.glob(file_path)

    if not file:
        print('No se han encontrado ningun archivo')
        return None
    
    return max(file, key=os.path.getctime)


def main():
    anomalies = {
    "synthetic_anomaly_vacuum_leak_*.csv": "vacuum_scaled.csv",
    "synthetic_anomaly_coolant_leak_*.csv": "coolant_scaled.csv",
    "synthetic_anomaly_sensor_drift_*.csv": "drift_scaled.csv"
    }  
    scaler = joblib.load('src/processing/scaler_healthy.pkl')

    for csv, scaled_csv in anomalies.items():
        latest_file = get_latest_file(csv) #cojemos el csv mas reciente
        latest_df = pd.read_csv(latest_file) #lo pasamos a dataframe
        bad_columns = ['timestamp', 'Distance (m)', 'average_fuel'] #las columnas que hay que eliminar 
        latest_df = latest_df.drop(columns=bad_columns) #se quitan esas columnas
        scaled_ndarray = scaler.transform(latest_df) #usamos transform en lugar de fit_transform()
        scaled_df = pd.DataFrame(scaled_ndarray, columns=latest_df.columns) #pasamos de Ndarray a DataFrame
        route = 'data/processed/'+ scaled_csv
        scaled_df.to_csv(route, index=False) #y luego a csv para guardarlo



if __name__=="__main__":
    main()
        

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
        #print('Descripción del DataFrame (sin timestamp ni segment_file):', df_diff.describe())
        scaled_ndarray = scaler.transform(df_diff_dropped)
        df_scaled = pd.DataFrame(scaled_ndarray, columns=df_diff_dropped.columns) #pasamos de Ndarray a DataFrame
        df_scaled.insert(0, 'timestamp', df_diff['timestamp'].values)
        #print('Descripción del DataFrame escalado:', df_scaled.describe())

        ruta_guardar = os.path.join('data/processed/test/' , 'diff_scaled_' + nombre_archivo)
        df_scaled.to_csv(ruta_guardar, index = False)


if __name__ == "__main__":
    main()

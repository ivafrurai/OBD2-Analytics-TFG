import pandas as pd
import os
import glob
from sklearn.preprocessing import StandardScaler
import joblib
from src.processing.feature_engineering import add_temporal_features


def scale_dataset(df):
    scaler = StandardScaler()
    scaled_ndarray = scaler.fit_transform(df)
    joblib.dump(scaler, 'src/processing/scaler_healthy.pkl')
    scaled_df = pd.DataFrame(scaled_ndarray, columns= df.columns)
    return scaled_df

def main():
    print("Buscando archivos CSV mas reciente...")

    df = pd.read_csv('data/raw/real_dataset.csv') #cargamos el csv sano

    df_con_diff = add_temporal_features(df) #añadimos las features temporales al csv sano

    df_con_diff.to_csv('data/processed/healthy_diff.csv', index=False) # se guarda el csv con las features temporales
    print('Columnas del DataFrame:', df_con_diff.columns.tolist())

    df_con_diff = df_con_diff.drop(columns=['timestamp', 'segment_file']) #quitamos la columna timestamp y segment_file para el escalado
    print('Descripción del DataFrame (sin timestamp ni segment_file):', df_con_diff.describe())

    scaled_df = scale_dataset(df_con_diff) #escalamos el csv con las features temporales
    print('Descripción del DataFrame escalado:', scaled_df.describe())
    scaled_df.to_csv('data/processed/healthy_diff_scaled.csv', index=False)# se guarda el csv con las features temporales escaladas



if __name__=="__main__":
    main()

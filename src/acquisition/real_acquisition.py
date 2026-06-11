import pandas as pd
import os
import glob
import joblib

def funcion():
    csv = pd.read_csv('data/raw/dataset.csv')
    df = pd.DataFrame(csv)
    df = df.drop(columns=['OBD_STATUS'])
    df = df[df['ABSOLUTE_LOAD'] <= 200]
    df = df.dropna(axis=1, how='all')
    df = df.ffill().bfill()
    df = df.dropna()
    columnas = {'RPM': 'rpm',
    'SPEED': 'speed',
    'ENGINE_LOAD': 'engine_load',
    'COOLANT_TEMP': 'coolant_temp',
    'MAF': 'MAF',
    'SHORT_FUEL_TRIM_1': 'stft',
    'LONG_FUEL_TRIM_1': 'ltft',
    'REAL_FUEL_USAGE_ML_MIN': 'fuel_instant',
    'THROTTLE_POS': 'throttle_position',
    'ACCELERATOR_POS_D': 'aceleration'}
    df = df.rename(columns=columnas)
    df_final = df[(['timestamp'] + ['segment_file']+ list(columnas.values()))]
    print(df_final.columns)
    df_final.to_csv('data/raw/real_dataset.csv', index=False)

    test_dir = os.path.join('data', 'raw', 'test')
    df_final.head(60000).to_csv(os.path.join(test_dir, 'test_healthy.csv'), index=False)

if __name__=="__main__":
    funcion()
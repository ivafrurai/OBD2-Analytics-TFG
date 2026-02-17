import pandas
import os
import glob
from sklearn.preprocessing import StandardScaler
import joblib


def get_latest_file(pattern):
    file_path =  os.path.join('data', 'raw', pattern)
    file = glob.glob(file_path)

    if not file:
        print('No se han encontrado ningun archivo')
        return None
    
    return max(file, key=os.path.getctime)

def scale_dataset(df):
    scaler = StandardScaler()
    scaled_ndarray = scaler.fit_transform(df)
    joblib.dump(scaler, 'src/processing/scaler_healthy.pkl')
    scaled_df = pandas.DataFrame(scaled_ndarray, columns= df.columns)
    return scaled_df

def main():
    print("Buscando archivos CSV mas reciente...")
    file_healthy_str = get_latest_file("synthetic_healthy_*.csv") #se coje el csv sano 
    df_healthy = pandas.read_csv(file_healthy_str)# se pasa a DataFrame
    print(df_healthy.columns.tolist())
    bad_columns = ['timestamp', 'Distance (m)', 'average_fuel'] #se eliminan las columnas que dependen del humano
    df_healthy = df_healthy.drop(columns=bad_columns)
    print(df_healthy.columns.tolist())

    healthy_scaled_df = scale_dataset(df_healthy)
    print(type(healthy_scaled_df))
    healthy_scaled_df.to_csv('data/processed/healthy_scaled.csv', index=False)



if __name__=="__main__":
    main()
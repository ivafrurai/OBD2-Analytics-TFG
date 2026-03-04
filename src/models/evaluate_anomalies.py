import pandas as pd
import joblib
import os
import glob


def evaluar_anomalias():
    anomalies = {
        "data/processed/vacuum_scaled.csv": "vacuum.csv",
        "data/processed/coolant_scaled.csv": "coolant.csv",
        "data/processed/drift_scaled.csv": "drift.csv"
    }
    model = joblib.load('src/models/sentinel_model.pkl')
    for csv, scaled_csv in anomalies.items():
        archivo= pd.read_csv(csv)
        predicciones = model.predict(archivo)
        archivo['anomaly'] = predicciones
        primer_fallo = archivo[archivo['anomaly']==-1].index[0]
        print(f'La avería en el archivo {scaled_csv} se produce en el segundo {primer_fallo}')
        print(archivo['anomaly'].head(30).values)


if __name__ == "__main__":
    evaluar_anomalias()
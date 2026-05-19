import numpy as np
import pandas as pd


def inyectar_error(df, fila_inicio, duracion, tipo):
    df_copy = df.copy()
    final = fila_inicio + duracion
    L = final - fila_inicio + 1  

    if tipo == 'embrague':
        #El motor se revoluciona, la velocidad no sube, entra mucho aire.
        df_copy.loc[fila_inicio:final, 'throttle_position'] = 90.0 + np.random.normal(0, 1, L) # Pedal a fondo
        df_copy.loc[fila_inicio:final, 'rpm'] = df_copy.loc[fila_inicio:final, 'rpm'] * 1.8 + np.random.normal(0, 80, L)
        df_copy.loc[fila_inicio:final, 'speed'] = df_copy.loc[fila_inicio:final, 'speed'] * 0.95 # Pierde inercia
        df_copy.loc[fila_inicio:final, 'engine_load'] = df_copy.loc[fila_inicio:final, 'engine_load'] * 0.7 + np.random.normal(0, 3, L) # La carga  se reduce
        df_copy.loc[fila_inicio:final, 'MAF'] = df_copy.loc[fila_inicio:final, 'MAF'] * 1.6 # Cuantas más RPM , más aire se aspira
        df_copy.loc[fila_inicio:final, 'fuel_instant'] = df_copy.loc[fila_inicio:final, 'fuel_instant'] * 1.5

    elif tipo == 'misfire':
        df_copy.loc[fila_inicio:final, 'stft'] = df_copy.loc[fila_inicio:final, 'stft'] + 35.0 + np.random.normal(0, 3, L)
        df_copy.loc[fila_inicio:final, 'rpm'] = df_copy.loc[fila_inicio:final, 'rpm'] + np.random.normal(0, 250, L)
        
        df_copy.loc[fila_inicio:final, 'engine_load'] = df_copy.loc[fila_inicio:final, 'engine_load'] * 0.70 + np.random.normal(0, 5, L)
        df_copy.loc[fila_inicio:final, 'MAF'] = df_copy.loc[fila_inicio:final, 'MAF'] * 0.75 + np.random.normal(0, 2, L)
        
        df_copy.loc[fila_inicio:final, 'speed'] = df_copy.loc[fila_inicio:final, 'speed'] * 0.95 + np.random.normal(0, 1.5, L)
        if 'aceleration' in df_copy.columns:
            df_copy.loc[fila_inicio:final, 'aceleration'] = df_copy.loc[fila_inicio:final, 'aceleration'] - 3.0 + np.random.normal(0, 4, L)
        
        df_copy.loc[fila_inicio:final, 'throttle_position'] = np.clip(df_copy.loc[fila_inicio:final, 'throttle_position'] * 1.4 + np.random.normal(0, 2, L), 0, 100.0)
        if 'fuel_instant' in df_copy.columns:
            df_copy.loc[fila_inicio:final, 'fuel_instant'] = df_copy.loc[fila_inicio:final, 'fuel_instant'] * 1.6 + np.random.normal(0, 1, L)
            
        df_copy.loc[fila_inicio:final, 'coolant_temp'] = df_copy.loc[fila_inicio:final, 'coolant_temp'] + np.random.normal(0, 0.5, L)

    elif tipo == 'sensor_maf':
        # FÍSICA: Descorrelación electrónica. Coche a fondo, pero el sensor lee un hilillo de aire.
        df_copy.loc[fila_inicio:final, 'MAF'] = 1.8 + np.random.normal(0, 0.1, L) # Lectura casi muerta
        df_copy.loc[fila_inicio:final, 'throttle_position'] = 85.0 + np.random.normal(0, 1, L)
        df_copy.loc[fila_inicio:final, 'rpm'] = 3500.0 + np.random.normal(0, 45, L) # El ruido salva las derivadas temporales
        df_copy.loc[fila_inicio:final, 'engine_load'] = 85.0 + np.random.normal(0, 2, L)
        df_copy.loc[fila_inicio:final, 'stft'] = 24.0 + np.random.normal(0, 1, L) # STFT altísimo porque la ECU intenta corregir la mezcla pobre

    elif tipo == 'coolant_temp':
        # La ECU corta inyección para salvar el bloque.
        df_copy.loc[fila_inicio:final, 'coolant_temp'] = 140.0 + np.random.normal(0, 0.5, L)
        df_copy.loc[fila_inicio:final, 'engine_load'] = 15.0 + np.random.normal(0, 2, L) # Carga estrangulada
        df_copy.loc[fila_inicio:final, 'rpm'] = 1500.0 + np.random.normal(0, 50, L) # Revs limitadas
        df_copy.loc[fila_inicio:final, 'throttle_position'] = df_copy.loc[fila_inicio:final, 'throttle_position'] * 0.3
        df_copy.loc[fila_inicio:final, 'MAF'] = 5.0 + np.random.normal(0, 0.5, L)
        df_copy.loc[fila_inicio:final, 'speed'] = df_copy.loc[fila_inicio:final, 'speed'] * 0.7 # El coche frena

    elif tipo == 'fuga_vacio':
        df_copy.loc[fila_inicio:final, 'MAF'] = df_copy.loc[fila_inicio:final, 'MAF'] * 0.2 + np.random.normal(0, 0.2, L)
        df_copy.loc[fila_inicio:final, 'engine_load'] = df_copy.loc[fila_inicio:final, 'engine_load'] * 0.9 + np.random.normal(0, 2, L)
        
        df_copy.loc[fila_inicio:final, 'stft'] = 35.0 + np.random.normal(0, 1, L) 
        df_copy.loc[fila_inicio:final, 'rpm'] = df_copy.loc[fila_inicio:final, 'rpm'] + np.random.normal(0, 120, L)
        
    return df_copy


if __name__ == "__main__":

    df_original = pd.read_csv('data/raw/real_dataset.csv')

    df_embrague = inyectar_error(df_original, 3000, 1000, tipo='embrague')
    df_embrague.to_csv('data/raw/test/test_embrague.csv', index = False)

    df_misfire = inyectar_error(df_original, 3000, 1000, tipo='misfire')
    df_misfire.to_csv('data/raw/test/test_misfire.csv', index = False)

    df_sensor_maf = inyectar_error(df_original, 3000, 1000, tipo='sensor_maf')
    df_sensor_maf.to_csv('data/raw/test/test_sensor_maf.csv', index = False)

    df_coolant_temp = inyectar_error(df_original, 3000, 1000, tipo='coolant_temp')
    df_coolant_temp.to_csv('data/raw/test/test_coolant_temp.csv', index = False)

    df_fuga_vacio = inyectar_error(df_original, 3000, 1000, tipo='fuga_vacio')
    df_fuga_vacio.to_csv('data/raw/test/test_fuga_vacio.csv', index = False)



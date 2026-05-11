import numpy as np
import pandas as pd



def inyectar_error(df, fila_inicio, duracion, tipo):

    df_copy = df.copy()
    final = fila_inicio + duracion

    if tipo == 'embrague':
        df_copy.loc[fila_inicio:final, 'rpm'] = df_copy.loc[fila_inicio:final, 'rpm'] * 1.4
        df_copy.loc[fila_inicio:final, 'speed'] = df_copy.loc[fila_inicio:final, 'speed'] * 0.8
        df_copy.loc[fila_inicio:final, 'throttle_position'] = 80.0

    elif tipo == 'misfire':
        ruido_vibracion = np.random.normal(0,150, duracion + 1)
        df_copy.loc[fila_inicio:final, 'rpm'] += ruido_vibracion
        df_copy.loc[fila_inicio:final, 'stft'] += 15.0

    elif tipo == 'sensor_maf':
        df_copy.loc[fila_inicio:final, 'MAF'] = df_copy.loc[fila_inicio:final, 'MAF']*0.6

    elif tipo == 'coolant_temp':
        df_copy.loc[fila_inicio:final, 'coolant_temp'] = 115.0

    elif tipo == 'fuga_vacio':
        df_copy.loc[fila_inicio:final, 'stft'] = 25.0 + np.random.normal(0,2, duracion + 1)
        
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



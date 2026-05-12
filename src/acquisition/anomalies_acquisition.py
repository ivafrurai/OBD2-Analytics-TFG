import numpy as np
import pandas as pd



def inyectar_error(df, fila_inicio, duracion, tipo):

    df_copy = df.copy()
    final = fila_inicio + duracion

    if tipo == 'embrague':
        df_copy.loc[fila_inicio:final, 'rpm'] = df_copy.loc[fila_inicio:final, 'rpm'] * 2.5 #se doblan las revoluciones 
        df_copy.loc[fila_inicio:final, 'speed'] = df_copy.loc[fila_inicio:final, 'speed'] * 0.2 #se baja la velocidad (si suben las rev es que patina el embrague )
        df_copy.loc[fila_inicio:final, 'throttle_position'] = 90.0 #todo esto ocurre cuando se esta acelerando

    elif tipo == 'misfire':
        ruido_vibracion = np.random.normal(0,250, duracion + 1)  
        df_copy.loc[fila_inicio:final, 'rpm'] += ruido_vibracion  #el missfire ocurrre cuando no hay buena combustion,
        df_copy.loc[fila_inicio:final, 'stft'] += 20.0            #es por eso que las rev vibran y el stft se dispara

    elif tipo == 'sensor_maf':
        df_copy.loc[fila_inicio:final, 'MAF'] = df_copy.loc[fila_inicio:final, 'MAF']*0.1   #El motor puede estar bajo mucha carga (subiendo una cuesta), 
        df_copy.loc[fila_inicio:final, 'rpm'] = 3500.0                                      #lo que requiere mucho aire, pero el MAF informa de un valor de ralentí. 
        df_copy.loc[fila_inicio:final, 'engine_load'] = 85.0                                #Esa contradicción de flujo es lo que la IA detecta como anómalo.


    elif tipo == 'coolant_temp':
        df_copy.loc[fila_inicio:final, 'coolant_temp'] = 140.0                                      #La ECU entra en modo protección. Baja la carga (Engine Load) y limita las RPM 
        df_copy.loc[fila_inicio:final, 'engine_load'] = 10.0                                        #para salvar el motor. La combinación de temperatura extrema con un rendimiento 
        df_copy.loc[fila_inicio:final, 'rpm'] = 1200.0 + np.random.normal(0,300, duracion + 1)      #capado es la "huella dactilar" del calentón.
        df_copy.loc[fila_inicio:final, 'stft'] = 30.0
        df_copy.loc[fila_inicio:final, 'MAF'] = 1.5


    elif tipo == 'fuga_vacio':
        df_copy.loc[fila_inicio:final, 'stft'] = 25.0 + np.random.normal(0,2, duracion + 1)  #se cuela aire al motor, y para equilibrar la mezcla pobre
                                                                                             #el stft sube casi al maximo.
        
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



import sys 
import os 
import random
import time 

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.acquisition.obd_simulator import OBDSimulator
from src.collection.data_logger import DataLogger

class OBDFaultInjector(OBDSimulator):
    def __init__(self, fault_type = 'none'):
        super().__init__()
        self.fault_type = fault_type
        print(f"Simulador iniciando en modo FALLO: {self.fault_type}")

    def update_physics(self, dt=0.1):
        super().update_physics(dt)

        #INYECCION DE FALLOS
        if self.fault_type == 'vacuum_leak': #fuga de vacio (entra aire no medido)
            self.stft += random.uniform(10,25) # el fuel trim se dispara un 20%
            self.ltft += 0.05 # el ltlf va aprendiendo poco a poco.

            if self.speed < 5:
                self.rpm += random.uniform(-50,50) # a ralentí el motor se vuelve inestable y puede subir o bajar de vueltas

        elif self.fault_type == 'coolant_leak':
            self.coolant_temp += 0.1 *dt # la temperatura sube 1 grado cada 10 segundos, bastante rapido

        elif self.fault_type == 'sensor_drift': #sensor MAF sucio o roto    
            # Recalculamos el MAF teórico limpio para tener una referencia base
            theoretical_maf = (self.rpm * (self.engine_load / 100.0)) / 50.0
            
            # Aplicamos la deriva: El sensor lee la MITAD de lo que debería (Factor 0.5)
            # Le sumamos ruido para que parezca un sensor real
            drifted_maf = (theoretical_maf * 0.5) + random.uniform(-0.1, 0.1)
            
            # Sobreescribimos la variable self.MAF brutalmente
            self.MAF = max(1.0, drifted_maf)

if __name__ == "__main__":

    # Opciones: 'vacuum_leak', 'coolant_leak', 'sensor_drift'
    AVERIA_ELEGIDA = 'vacuum_leak'

    simulador = OBDFaultInjector(fault_type=AVERIA_ELEGIDA)
    logger = DataLogger(prefix=f"synthetic_anomaly_{AVERIA_ELEGIDA}")

    try:
        while True:
            simulador.update_physics(0.1)
            data = simulador.get_data()
            logger.log(data)

            print(f" FALLO ACTIVO: {AVERIA_ELEGIDA} | STFT: {data['stft']:.1f} | Temp: {data['coolant_temp']:.1f}", end='\r')
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.close()
        print("Simulación terminada.")
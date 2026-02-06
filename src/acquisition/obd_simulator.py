import os
import sys
import time
import random
from datetime import datetime 
import math 

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)
from src.collection.data_logger import DataLogger

class OBDSimulator:
    def __init__(self):
        #Parametros basicos 
        self.rpm = 800.0
        self.speed = 0.0
        self.throttle_pos = 0.0
        self.brake_pos = 0.0
        self.engine_load = 20.0    #porcentaje de la capacidad del motor que se esta usando
        self.coolant_temp = 25.0

        #Parametros avanzados
        self.MAF = 3.0 #Flujo de aire en g/seg, es 3 porque un motor aspira unos 3 g/s a 800 rpm
        self.stft = 0.0 #Short term fuel trim, indica si el motor esta inyectando mas o menos gasolina de la teorica.
        self.ltft = 0.0 #Long term fuel trim

        #Calculos derivados
        self.distance = 0.0
        self.acceleration = 0.0
        self.fuel_instant = 0.0
        self.fuel_average = 7.5

        #Variables de control
        #self.last_update_time = time.time() #marca de tiempo para calcular la derivada
        self.target_speed = 0.0
        self.fuel_buffer = [] #buffer para el calculo de medias
        self.time_counter = 0.0 #reloj interno continuo para la oscilacion de sensores


    def update_physics(self, dt=0.1):

        self.time_counter += dt

        #SIMULA EL CONDUCTOR
        if random.random() < 0.05: #el 0.05 simula que el conductor toma una decision nueva cada 20 ciclos (4-10s).
            action = random.choice(['acceleration', 'brake', 'coast']) #coast es dejarse llevar, ni acelerar ni frenar

            if action == 'brake':
                self.brake_pos = min(100, self.brake_pos + random.uniform(5,20))
                self.throttle_pos = 0
            
            elif action == 'acceleration':
                self.throttle_pos = min(100, self.throttle_pos + random.uniform(1,10)) #el random unifform es mas pequeño porque el acelerador se pisa de forma mas progresiva y suave.
                self.brake_pos = 0

            else:
                self.throttle_pos = max(0, self.throttle_pos -45) #45 porque el pedal debe bajar rapido, no se pone 100 porque la derivada seria -infinito.
                self.brake_pos = max(0, self.brake_pos -35)

        #simula el ruido
        self.throttle_pos = max(0.0, min(100.0, self.throttle_pos + random.uniform(-1, 1)))
        self.brake_pos = max(0.0, min(100.0, self.brake_pos + random.uniform(-1, 1)))

        if self.brake_pos > 1.0: 
            self.throttle_pos = 0.0
        elif self.throttle_pos > 0.0:
            self.brake_pos = 0.0
        #MOTOR Y MAF
        if self.coolant_temp < 60:
            warmup_factor = (60 - self.coolant_temp) / 40.0 #el 40 es la diferencia entre frio(20º) y caliente(60º)
            warmup_factor = max(0.0, min(1.0, warmup_factor))
            base_idle = 800 + (300*warmup_factor) #el 300 es la constante de calibracion, es la diferencia entre 1100 y 800 rpm.
        else:
            base_idle = 800.0

        target_rpm = base_idle + (self.throttle_pos * 60) #el 60 es un factor de calibracion para que a tope de acelerador el motor llegue a unas rpm razonables.

        if self.brake_pos>0:
            target_rpm = base_idle #esto simula que coges el embrague y las revoluciones bajan al minimo.
        
        self.rpm = (self.rpm * 0.9) + (target_rpm * 0.1) + random.uniform(-5,5)
        self.rpm = max(base_idle, self.rpm)

        self.engine_load = (self.throttle_pos * 0.8) + 15 + random.uniform(-1,1) #el 15 es una carga minima del motor en ralentí, contando con friccion y eso

        base_maf = (self.rpm * (self.engine_load/100)) /50 #el 50 es una constante de calibracion para que a 800 rpm y carga 20% el MAF sea 3 g/s
        self.MAF = max(2.0, base_maf + random.uniform(-0.5,0.5)) #agrega ruido al MAF, con un minimo de 2 g/s

        #FUEL TRIMS
        oscillation = math.sin(self.time_counter*2)*3  #el 3 es el % que varia el stft, el 2 es la velocidad de oscilacion
        noise = random.uniform(-2,2)
        self.stft = oscillation + noise #el stft oscila rapido alrededor de 0


        self.ltft = (self.ltft * 0.99) + (self.stft*0.01) #el ltft sigue al stft muy lentamente, si el stft es positivo mucho tiempo, el ltft sube para compensar.


        #MOVIMIENTO 
        last_speed_ms = self.speed / 3.6 #convertimos a m/s para el calculo de aceleracion
        gear_ratio_speed = self.rpm / 55.0  # Relación de marcha simulada

        if self.brake_pos > 0: 
            # Si frena, el objetivo es bajar velocidad drásticamente
            # Multiplicamos por un factor para que el freno tenga "fuerza"
            braking_force = self.brake_pos * 0.5 
            self.target_speed = max(0, self.speed - braking_force)
            
        elif self.throttle_pos == 0 and self.speed < 15:
            # Simulación de embrague pisado al llegar a semáforo
            self.target_speed = 0.0
            
        else:
            # Si acelera o mantiene, la velocidad depende de las RPM
            self.target_speed = gear_ratio_speed
        
        # 3. APLICAR INERCIA (Suavizado para simular la masa del coche)
        # Ajuste fino: Si ves que la aceleración da picos muy altos, baja el 0.05 a 0.02
        if self.target_speed > self.speed:
            # Acelerando: La masa se opone al cambio (factor 0.05)
            self.speed = (self.speed * 0.98) + (self.target_speed * 0.02)
        else:
            # Decelerando: El freno/rozamiento actúa (factor 0.05 para que no sea un frenazo en seco)
            self.speed = (self.speed * 0.95) + (self.target_speed * 0.05)

        # 4. FOTO ACTUAL
        current_speed_ms = self.speed / 3.6

        # 5. CÁLCULO DE ACELERACIÓN (Con protección anti-crash)
        if dt > 0.001:  # Evitamos dividir por 0 o números infinitesimales
            self.acceleration = (current_speed_ms - last_speed_ms) / dt
        else:
            self.acceleration = 0.0

        # 6. ACTUALIZAR ODOMETRO
        self.distance += current_speed_ms * dt

        #consumo y combustible
        correction_factor = 1.0 + (self.stft / 100.0)
        fuel_l_h = ((self.MAF * 3600) / (14.7 * 740)) * correction_factor # 14.7 es Relación Estequiométrica (AFR) de la Gasolina, 3600 es para convertir de g/s a g/h, 740 es la densidad de la gasolina.

        if self.throttle_pos == 0 and self.rpm > 1100: #El Ahorrador (DFCO), esto apaga los inyectores.
            fuel_l_h = 0.0

        if self.speed < 5:
            self.fuel_instant = fuel_l_h
        else:
            self.fuel_instant = (fuel_l_h /self.speed) *100 #para convertir en L/100km.

        self.fuel_buffer.append(self.fuel_instant)
        if len(self.fuel_buffer) > 100: #mantenemos en memoria los ultimos 100 datos.
            self.fuel_buffer.pop(0)
        if len(self.fuel_buffer) > 0:
            self.fuel_average = sum(self.fuel_buffer) / len(self.fuel_buffer) #se calcula el consumo medio.

        
        #temperatura
        if self.coolant_temp < 90: self.coolant_temp +=0.05
        else: self.coolant_temp+= random.uniform(-0.2,0.2)




    def get_data(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "rpm": int(self.rpm),
            "speed": int(self.speed),
            "engine_load": round(self.engine_load,1),
            "coolant_temp": round(self.coolant_temp, 1),
            "MAF": round(self.MAF,2),
            "stft": round(self.stft,1),
            "ltft": round(self.ltft,1),
            "fuel_instant": round(self.fuel_instant,1),
            "average_fuel": round(self.fuel_average,1),
            "throttle_position": int(self.throttle_pos),
            "brake_position": int(self.brake_pos),
            "aceleration": round(self.acceleration,1),
            "Distance (m)": round(self.distance,1)
        }
    
if __name__ == "__main__":
    print("Simulando Motor...")
    simulator = OBDSimulator()
    logger = DataLogger(prefix='synthetic_healthy')
    try:
        while True:
            simulator.update_physics(0.1)
            data = simulator.get_data()
            logger.log(data)
            output = " | ".join([f"{key}: {value}" for key, value in data.items()])
            print("-"*150)
            print(output)
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.close()
        print("Simulación terminada.")
import time
import random
from datetime import datetime   

class OBDSimulator:
    def __init__(self):
        self.rpm = 800.0
        self.speed = 0.0
        self.throttle = 0.0
        self.engine_load = 20.0
        self.coolant_temp = 25.0

        self.target_speed = 0.0


    def update_physics(self):

        #simula el acelerador cambiando poco a poco(de 5 en 5%);
        change = random.uniform(-5, 5) 
        self.throttle = max(0, min(100, self.throttle + change))

        #las rmp siguen al acelerador
        target_rpm = 800 + (self.throttle * 50)

        #el motor tarda en subir de rpm
        self.rpm = (self.rpm * 0.9) + (target_rpm * 0.1)

        #se añade ruido natural.
        noise = random.uniform(-15,15)
        self.rpm = max(0, self.rpm + noise)

        #calcular velocidad, se establece una relacion 2000rpm->33km/h
        self.target_speed = self.rpm /60.0

        #el coche tarde en subir de velocidad
        self.speed = (self.speed * 0.95) + (self.target_speed * 0.05)

        #la temperatura sube a 90º y luego va oscilando 0.5º
        if self.coolant_temp < 90:
            self.coolant_temp += 0.1
        else:
            self.coolant_temp += random.uniform(-0.5, 0.5)


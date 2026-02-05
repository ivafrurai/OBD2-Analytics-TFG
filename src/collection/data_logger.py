import csv
import time 
import os 

class DataLogger:
    def __init__(self, prefix = 'log'):
        if not os.path.exists('data/raw'):
            os.makedirs('data/raw')

        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        self.filename = f"data/raw/{prefix}_{timestamp_str}.csv"

        self.file  = open(self.filename, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.headers_written = False
        print(f"Grabando datos en el archivo {self.filename}.")


    def log(self, data_dict): #recibe un dicionario con las variables y sus valores y lo guarda.
        if not self.headers_written: 
            headers = list(data_dict.keys())
            self.writer.writerow(headers)
            self.headers_written = True

        values = list(data_dict.values())
        self.writer.writerow(values)

        self.file.flush() #para asegurarnos de que los datos se escriben en el disco inmediatamente.

    def close(self):
        self.file.close()
        print("Grabación finalizada, archivo cerrado.")
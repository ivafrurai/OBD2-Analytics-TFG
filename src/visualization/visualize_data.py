import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import sys

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale = 1.5)

def get_latest_file(pattern):
    file_path =  os.path.join('data', 'raw', pattern)
    file = glob.glob(file_path)

    if not file:
        print('No se han encontrado ningun archivo')
        return None
    
    return max(file, key=os.path.getctime)

def plot_vacuum_leal(df_healthy, df_faulty):
    print("Generando grafica para la fuga de vacío...")
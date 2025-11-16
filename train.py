"""
Path: train.py
"""

import os
import shutil
import subprocess

# Rutas
models_dir = os.path.join(os.getcwd(), "rasa_project", "models")
config_path = os.path.join("rasa_project", "config.yml")
domain_path = os.path.join("rasa_project", "domain.yml")
data_path = os.path.join("rasa_project", "data")

# Eliminar modelos anteriores si existen
if os.path.exists(models_dir):
    shutil.rmtree(models_dir)
    print("Modelos anteriores eliminados.")

# Comando de entrenamiento
cmd = [
    "rasa",
    "train",
    "--config",
    config_path,
    "--domain",
    domain_path,
    "--data",
    data_path,
    "--out",
    models_dir,
]

# Ejecutar el comando y mostrar la salida en tiempo real
process = subprocess.Popen(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)

print("Entrenando modelo... (esto puede tardar unos minutos)\n")
for line in process.stdout:
    print(line, end="")  # Mostrar cada línea a medida que llega

process.wait()

if process.returncode != 0:
    print("\nEl entrenamiento falló. Revisa los mensajes anteriores.")
else:
    print("\nEntrenamiento completado exitosamente.")

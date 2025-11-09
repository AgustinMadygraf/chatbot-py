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
    "rasa", "train",
    "--config", config_path,
    "--domain", domain_path,
    "--data", data_path,
    "--out", models_dir
]

# Ejecutar el comando
result = subprocess.run(cmd, capture_output=True, text=True, check=False)

print(result.stdout)
if result.stderr:
    print("Errores:", result.stderr)
import os
import urllib.request
import shutil
import time
from pathlib import Path

url = "https://github.com/tensorflow/tensorflow/archive/refs/tags/v2.20.0.zip"
destination_folder = Path.home() / "Downloads"
file_name = "telechargement.zip"

iteration = 0
while True :
    try :
        unique_file_name = f"{file_name.replace('.zip', '')}_{iteration}.zip"
        file_path = os.path.join(destination_folder, unique_file_name)
        with urllib.request.urlopen(url) as response, open(file_path, "wb") as f:
            while True:
                chunk = response.read(8192)  # Lit par blocs de 8 Ko
                if not chunk:
                    break
                f.write(chunk)

        print(f"Fichier téléchargé : {unique_file_name}")
        iteration += 1
        time.sleep(0.1)
    except Exception as e:
        # Affiche l'erreur (ex: "No space left on device")
        print(f"Erreur à l'itération {iteration} : {e}")
        iteration += 1
        time.sleep(1) 
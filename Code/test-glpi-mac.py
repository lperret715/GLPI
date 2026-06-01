import os
import platform
import subprocess
import sys 
import tempfile
from pathlib import Path

SERVER="https://micronov.fr36.glpi-network.cloud"
AGENT_MAC="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
DEBUG = True



PATH_DESKTOP = Path.home() / "Desktop"
AGENT_PKG_PATH = DESKTOP_PATH / "GLPI-Agent.pkg"
CONFIG_DIR = Path("/Applications/GLPI-Agent/etc/conf.d")
CONFIG_PATH = CONFIG_DIR / "glpi.cfg"


MISSING_DEPS = []
REQUIRED_DEPS = ["curl", "installer"]
# tag = input("Tag : ")

# fichier_config = f"""
# server = {SERVER}
# debug=1
# tag = {tag}
# """



def log(message,error) :
    prefix = "❌ [ERREUR]" if error else "✅ [INFO]"
    print(f"{prefix} {message}")

def check_dependencies() : 
    MISSING_DEPS = []
    for dep in REQUIRED_DEPS :
        try :
            subprocess.run(
                ["which", dep],
                check = True,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError :
            MISSING_DEPS.append(dep)
    if MISSING_DEPS :
        log(f"Dépendances manquantes : {','.join(MISSING_DEPS)}", True)
        return False
    return True
        

def install_glpi_mac() : 
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as tmp:
        tmp.write(fichier_config)
        tmp_path = tmp.name
    
    command_mac = f"cd {PATH_DESKTOP} && curl -L -O {AGENT_MAC} && sudo installer -verbose -pkg {PATH_DESKTOP}/{os.path.basename(AGENT_MAC)} -target /Applications && sudo cp {tmp_path} {PATH_CONFIG} && sudo launchctl start com.teclib.glpi-agent && sudo /Applications/GLPI-Agent/bin/glpi-agent"   
    try : 
        subprocess.run(
            command_mac,
            check = True,
            shell = True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text = True
            )
        os.unlink(tmp_path)
        print(f"Commande exécutée avec succès : {command_mac}")
        print("✅ Installation terminée avec succès.")
    except subprocess.CalledProcessError as e :
        print(f"Erreur lors de l'installation : {e}")
        return

    return

def main():
    system=platform.system()
    if system == "Darwin" :
        print("Système détecté : Mac \n Démarrage de l'installation Mac")
        install_glpi_mac()
    else : 
        print(f"OS non supporté : {system}")

if __name__ == "__main__" : 
    main()




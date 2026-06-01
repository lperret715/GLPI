import os
import platform
import subprocess
import sys 
import tempfile
import urllib.request
from pathlib import Path

SERVER="https://micronov.fr36.glpi-network.cloud"
AGENT_MAC="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
DEBUG = True



AGENT_PKG_PATH = Path("/Applications") / "GLPI-Agent.pkg"
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


def install_dependencies() : 
    try :
        subprocess.run(
            ["sudo", "apt", "update"],
            check = True,
            stdout = subprocess.PIPE if not DEBUG else None,
        )
        subprocess.run(
            ["sudo", "apt", "install", "-y"] + MISSING_DEPS,
            check = True,
            stdout = subprocess.PIPE if not DEBUG else None
        )
        log("Dépendances installées avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log (f"Erreur lors de l'installation des dépendances : {e}", True)
        return False
    

def download_file(url, destination) :
    try :
        urllib.request.urlretrieve(url, destination)
        log(f"Fichier téléchargé : {destination.name}", False)
        return True
    except Exception as e :
        log(f"Echec du téléchargement : {e}", True)
        return False








#command_mac = f"cd {PATH_DESKTOP} && curl -L -O {AGENT_MAC} && sudo installer -verbose -pkg {PATH_DESKTOP}/{os.path.basename(AGENT_MAC)} -target /Applications && sudo cp {tmp_path} {PATH_CONFIG} && sudo launchctl start com.teclib.glpi-agent && sudo /Applications/GLPI-Agent/bin/glpi-agent"   

def install_glpi_mac() : 
    if not check_dependencies() :
        log("Installation des dépendances...", False)
        if not install_dependencies() :
            sys.exit(1)
    if not download_file(AGENT_MAC, AGENT_PKG_PATH) :
        sys.exit(1)
    
    
    
    
    # with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as tmp:
    #     tmp.write(fichier_config)
    #     tmp_path = tmp.name
    
    
    # try : 
    #     subprocess.run(
    #         command_mac,
    #         check = True,
    #         shell = True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text = True
    #         )
    #     os.unlink(tmp_path)
    #     print(f"Commande exécutée avec succès : {command_mac}")
    #     print("✅ Installation terminée avec succès.")
    # except subprocess.CalledProcessError as e :
    #     print(f"Erreur lors de l'installation : {e}")
    #     return

    # return


def main():
    tag = input("Tag : ")
    if not tag :
        log("Le tag ne peut pas être vide.", True)
        sys.exit(1)
    system=platform.system()
    if system == "Darwin" :
        print("Système détecté : Mac \n Démarrage de l'installation Mac")
        install_glpi_mac()
    else : 
        print(f"OS non supporté : {system}")
        sys.exit(1)

if __name__ == "__main__" : 
    main()




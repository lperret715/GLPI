import os
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path
import tempfile

SERVER="https://micronov.fr36.glpi-network.cloud"
AGENT_MAC="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
DEBUG = True



AGENT_PKG_PATH = Path("/Applications") / "GLPI-Agent.pkg"
CONFIG_DIR = Path("/Applications/GLPI-Agent/etc/conf.d")
CONFIG_PATH = CONFIG_DIR / "glpi.cfg"
AGENT_PATH = Path("/Applications/GLPI-Agent/bin/glpi-agent")
AGENT_NAME = "com.teclib.glpi-agent"


MISSING_DEPS = []
REQUIRED_DEPS = ["curl", "installer"]





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

def install_package(pkg) :
    cmd = [
        "sudo", "installer",
        "-verbose",
        "-pkg", pkg,
        "-target", pkg.parent
    ]
    try :
        subprocess.run(
            cmd, 
            check = True,
        )
        log("GLPI Agent installé avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"Erreur pendant l'installation : {e}", True)
        return False
    



def create_config(path, server, tag) :
    try :
        fichier_config = f"""
server = {server}
debug=1
tag = {tag}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete = False) as tmp_file :
            tmp_file.write(fichier_config)
            tmp_path = Path(tmp_file.name)
        cmd = [
            "sudo",
            "cp", tmp_path, path
        ]
        subprocess.run(cmd, check = True)
        log(f"Fichier de configuration créé avec succès", False)
        tmp_path.unlink()
        return True
    except Exception as e :
        log(f"Erreur lors de la création du fichier de configuration : {e}", True)
        if tmp_path.exists() :
            tmp_path.unlink()
        return False


def start_process(process) :
    cmd = [
        "sudo", "launchctl",
        "start", process
    ]
    try : 
        subprocess.run(cmd, check = True)
        log(f"{process} démarré avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"{process} n'a pas pu être démarré : {e}", True)
        return False
    
def agent_run(agent) :
    cmd = ["sudo", agent]
    try :
        subprocess.run(cmd, check = True)
        log(f"{agent} démarré avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"{agent} n'a pas pu être démarré : {e}", True)
        return False
    









# command_mac = f"cd {PATH_DESKTOP} && curl -L -O {AGENT_MAC} && sudo installer -verbose -pkg {PATH_DESKTOP}/{os.path.basename(AGENT_MAC)} -target /Applications && sudo cp {tmp_path} {PATH_CONFIG} && sudo launchctl start com.teclib.glpi-agent && sudo /Applications/GLPI-Agent/bin/glpi-agent"   

def install_glpi_mac(tag) : 
    try : 
        if not check_dependencies() :
            log("Installation des dépendances...", False)
            if not install_dependencies() :
                return False
        if not download_file(AGENT_MAC, AGENT_PKG_PATH) :
            return False
        if not install_package(AGENT_PKG_PATH) :
            return False
        if not create_config(CONFIG_PATH, SERVER, tag) :
            return False
        if not start_process(AGENT_NAME) :
            return False
        if not agent_run(AGENT_PATH) :
            return False
    finally : 
        if AGENT_PKG_PATH.exists() : 
            AGENT_PKG_PATH.unlink()
    return True


def main():
    tag = input("Tag : ")
    if not tag :
        log("Le tag ne peut pas être vide.", True)
        sys.exit(1)
    system=platform.system()
    if system == "Darwin" :
        print("Système détecté : Mac \n Démarrage de l'installation Mac")
        if not install_glpi_mac(tag) :
            sys.exit(1)
    else : 
        print(f"OS non supporté : {system}")
        sys.exit(1)

if __name__ == "__main__" : 
    main()




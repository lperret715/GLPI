import os
import platform
import subprocess
import sys
from pathlib import Path
import urllib.request



# ---------------- LIENS --------------------------------------------------------------------------------------------------
SERVER = "https://micronov.fr36.glpi-network.cloud"
MONITOR="https://github.com/glpi-project/glpi-agentmonitor/releases/download/1.5.0/GLPI-AgentMonitor-x64.exe"
AGENT_WINDOWS="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17-x64.msi"
AGENT_MAC="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
AGENT_LINUX="https://github.com/glpi-project/glpi-agent/releases/download/1.17/glpi-agent-1.17-linux-installer.pl"


#---------------- CONSTANTES -------------------------------------
DEBUG = True

# ---------------- CHEMINS -------------------------------------------------------------------------------------------------
DESKTOP = Path.home() / "Desktop"
AGENT_PATH= DESKTOP / "GLPI-Agent.msi"
MONITOR_PATH= DESKTOP / "GLPI-Agent-Monitor.exe"

#---------------- NOMS PACKAGES --------------------------------------------------------------------------------
WINGET_AGENT_NAME = "GLPI-Project.GLPI-Agent"
WINGET_MONITOR_NAME = "GLPI Agent Monitor"


def log(message,error) :
    prefix = "❌ [ERREUR]" if error else "✅ [INFO]"
    print(f"{prefix} {message}")


#Regarder si winget existe
def is_winget_installed():
    try:
        subprocess.run(
            ["winget", "--version"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

#Regarder si l'agent existe déjà
def is_package_installed(package_name):
    try:
        res = subprocess.run(
            ["winget", "list", "--id", package_name], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
            )
        return package_name in res.stdout
    except Exception:
        return False


#def install_winget() : 

#Désinstaller l'agent s'il existe (UNIQUEMENT POUR TESTS, A NE PAS CONSERVER DANS LE CODE FINAL)
def uninstall_package(package_name):
    if not is_package_installed(package_name):
        log(f"{package_name} n'est pas installé.", False)
        return True
    
    response = input (f"Voulez-vous désinstaller {package_name} ? (o/n) : ").strip().lower()
    if response != "o" : 
        log(f"Désinstallation de {package_name} annulée.", False)
        return True

    try:
        # Utilise une liste pour éviter les problèmes de guillemets
        cmd = [
            "winget", "uninstall", package_name,
            "-e", "--accept-source-agreements"
        ]
        subprocess.run(
            cmd, 
            check=True,
            )
        log(f"{package_name} désinstallé avec succès.", False)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Erreur pendant la désinstallation de {package_name} : {e}", True)
        return False

def download_file(url, destination) : 
    try :
        # command = [
        #     "powershell.exe",
        #     "-Command",
        #     f"Invoke-WebRequest -Uri '{url}' -Outfile '{destination}' -UseBasicParsing"    
        # ]
        # subprocess.run(
        #     command,
        #     check = True, 
        #     stdout = subprocess.PIPE if not DEBUG else None
        # )
        urllib.request.urlretrieve(url, destination)
        log (f"Fichier téléchargé : {destination.name}", False)
        return True
    except subprocess.CalledProcessError as e :
        log (f"Echec du téléchargement de {url} : {e}", True)
        return False



def install_msi(msi_path, server, tag) : 
    try : 
        command = [
            "msiexec.exe",
            "/i", str(msi_path),
            f"/qb SERVER={server} TAG={tag} RUNNOW=1",
        ]
        subprocess.run(
            command,
            check = True
        ) 
        log(f"Installation de {msi_path} terminée.", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"Echec de l'installation de {msi_path} : {e}", True)
        return False
    

def install_with_winget(package_name, custom_args) : 
    try : 
        command = [
            "winget", "install",
            package_name,
            "--custom", custom_args,
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
        subprocess.run(
            command,
            check = True,  
        )
        log(f"{package_name} installé avec succès", False)
        return True
    except subprocess.CalledProcessError as e : 
        log(f"Erreur lors de l'installation de {package_name} : {e}", True)
        return False

#Installation Windows
def install_glpi_windows(tag) :
    if not uninstall_package(WINGET_AGENT_NAME) : 
        return False
    if is_winget_installed() : 
        custom_args = f"SERVER={SERVER} TAG={tag} RUNNOW=1"
        return install_with_winget(WINGET_AGENT_NAME, custom_args)
    
    try : 
        if not download_file(AGENT_WINDOWS, AGENT_PATH) :
            return False
        if not install_msi(AGENT_PATH, SERVER, tag) :
            return False
    finally : 
        if AGENT_PATH.exists() : 
            AGENT_PATH.unlink()
    return True
        

def install_glpi_monitor():
    if not uninstall_package(WINGET_MONITOR_NAME) : 
        return False
    

    try :
        if not download_file(MONITOR, MONITOR_PATH) : 
            return False
    except Exception : 
        return False


def main():
    tag = input ("Tag : ")
    if not tag : 
        log("Le tag ne peut pas être vide.", True)
        sys.exit(1)
    system = platform.system()
    # if system == "Linux":
    #     install_glpi_linux()
    # elif system == "Darwin":
    #     install_glpi_macos()
    if system == "Windows":
        if not install_glpi_windows(tag) : 
           sys.exit(1)
        if not install_glpi_monitor() :
           sys.exit(1)
    else:
        print(f"OS non supporté : {system}")

if __name__ == "__main__":
    main()






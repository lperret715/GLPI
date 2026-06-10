import os
import sys
import platform
import tempfile
import subprocess
import urllib.request
from pathlib import Path

# ---------------- LIENS --------------------------------------------------------------------------------------------------

SERVER = "https://micronov.fr36.glpi-network.cloud"
AGENT_WINDOWS="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17-x64.msi"
AGENT_MAC="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
AGENT_LINUX="https://github.com/glpi-project/glpi-agent/releases/download/1.17/glpi-agent-1.17-linux-installer.pl"
MONITOR="https://github.com/glpi-project/glpi-agentmonitor/releases/download/1.5.0/GLPI-AgentMonitor-x64.exe" # Agent moniteur, permet sous Windows de donner des commandes à l'agent
DOCUMENTATION_LINUX = "https://glpi-agent.readthedocs.io/en/latest/installation/index.html#gnu-linux" # Lien vers la documentation de linux en cas d'échec de l'installation

#---------------- CONSTANTES -----------------------------------------------------------------------------------------------

DEBUG = True # Constante Débug pour log les potentiels problemes lors de l'installation
SUPPORTED_LINUX_DISTROS = ["redhat", "centos", "debian", "ubuntu"] # Distributions Linux supportées

# ---------------- CHEMINS -------------------------------------------------------------------------------------------------

#------Windows---------------------------------------

DESKTOP = Path.home() / "Desktop"
AGENT_WINDOWS_PATH= DESKTOP / "GLPI-Agent.msi"
MONITOR_WINDOWS_PATH= DESKTOP / "GLPI-Agent-Monitor.exe"

#--------Mac-------------------------------------------------------

AGENT_MAC_PKG_PATH = Path("/Applications") / "GLPI-Agent.pkg"
CONFIG_MAC_DIR = Path("/Applications/GLPI-Agent/etc/conf.d")
CONFIG_MAC_PATH = CONFIG_MAC_DIR / "glpi.cfg"
AGENT_MAC_PATH = Path("/Applications/GLPI-Agent/bin/glpi-agent")

#---------------- NOMS PACKAGES -----------------------------------------------------------------------------------------------

WINGET_AGENT_NAME = "GLPI-Project.GLPI-Agent"
WINGET_MONITOR_NAME = "GLPI Agent Monitor"
AGENT_LINUX_NAME = "glpi-agent-installer.pl"
AGENT_MAC_NAME = "com.teclib.glpi-agent"

#------------------------------ LISTE DES DEPENDANCES NECESSAIRES --------------------------------------------------------------------------------------

MISSING_DEPS = []
REQUIRED_LINUX_DEPS = ["perl", "libxml-libxml-perl", "libnet-ip-perl", "dmidecode"]
REQUIRED_MAC_DEPS = ["curl", "installer"]

#---------------------------- FONCTIONS COMMUNES A TOUS OS---------------------------------------------------------------------------------

#Afficher un message de validation ou d'erreur (error = True s'il y a une erreur, False sinon)
def log(message: str, error=True) :
    prefix = "❌ [ERREUR]" if error else "✅ [INFO]"
    print(f"{prefix} {message}")

#Télécharger un fichier via un url
def download_file(url: str, destination: str) :
    try :
        urllib.request.urlretrieve(url, destination)
        log (f"Fichier téléchargé : {destination.name}", False)
        return True
    # S'il y a une erreur on le signale directement
    except subprocess.CalledProcessError as e :
        log (f"Echec du téléchargement de {url} : {e}")
        return False

#Vérifier si les dépendances nécessaires à l'installation sont installées sur cette machine
def check_dependencies(missing_deps: list, required_deps: list) :
    missing_deps = []
    for dep in required_deps : 
        try :
            subprocess.run(
                ["which", dep],
                check = True,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError : 
            missing_deps.append(dep)
    if missing_deps : 
        log(f"Dépendances manquantes : {','.join(missing_deps)}")
        return False
    return True

#Si ce n'est pas le cas, installer les dépendances manquantes
def install_dependencies(missing_deps: list) : 
    try : 
        subprocess.run(
            ["sudo", "apt", "update"],
            check = True,
            stdout = subprocess.PIPE if not DEBUG else None,
        )
        subprocess.run(
            ["sudo", "apt", "install", "-y"] + missing_deps,
            check = True,
            stdout = subprocess.PIPE if not DEBUG else None,
        )
        log("Dépendances installées avec succès", False)
        return True
    except subprocess.CalledProcessError as e : 
        log(f"Echec de l'installation des dépendances : {e}")
        return False

#------------------------------------------------------ FONCTIONS NECESSAIRES A INSTALLATION WINDOWS --------------------------------------------------------------------------

#Regarder si l'agent existe déjà
def is_package_installed(package_name: str):
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

#Désinstaller l'agent s'il existe (UNIQUEMENT POUR TESTS, A NE PAS CONSERVER DANS LE CODE FINAL)
def uninstall_package(package_name: str):
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
        log(f"Erreur pendant la désinstallation de {package_name} : {e}")
        return False

#Installer un package msi 
def install_msi(msi_path: str, server: str, tag: str) : 
    try : 
        command = [
            "msiexec.exe",
            "/i", str(msi_path),
            "/qb",
            f"SERVER={server}",
            f"TAG={tag}",
            "FULL-INVENTORY-POSTPONE=0",
            "RUNNOW=1",
        ]
        subprocess.run(
            command,
            check = True
        ) 
        log(f"Installation de {msi_path} terminée.", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"Echec de l'installation de {msi_path} : {e}")
        return False

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

#installer un package via Winget (Bien plus rapide !)
def install_with_winget(package_name: str, custom_args: list) : 
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
        log(f"Erreur lors de l'installation de {package_name} : {e}")
        return False

#------------------------------------------------------ FONCTIONS NECESSAIRES A INSTALLATION MAC --------------------------------------------------------------------------



# Installer un package Mac
def install_package_mac(pkg: str) :
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
        log(f"Erreur pendant l'installation : {e}")
        return False


#Créer un fichier de configuration
def create_config_mac(path: str, server: str, tag: str) :
    try :
        #structure et contenu du fichier de config
        fichier_config = f"""
server = {server}
debug=1
full-inventory-postpone=0
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
        log(f"Erreur lors de la création du fichier de configuration : {e}")
        if tmp_path.exists() :
            tmp_path.unlink()
        return False

# Lancer un process
def start_process_mac(process: str) :
    cmd = [
        "sudo", "launchctl",
        "start", process
    ]
    try : 
        subprocess.run(cmd, check = True)
        log(f"{process} démarré avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"{process} n'a pas pu être démarré : {e}")
        return False

# Lancer l'agent    
def agent_run_mac(agent: str) :
    cmd = ["sudo", agent]
    try :
        subprocess.run(cmd, check = True)
        log(f"{agent} démarré avec succès", False)
        return True
    except subprocess.CalledProcessError as e :
        log(f"{agent} n'a pas pu être démarré : {e}")
        return False
    
# ------------------------------------------FONCTIONS NECESSAIRES A INSTALLATION LINUX --------------------------------------------------------------

# Obtenir la distribution de la machine (installation pas possible sur n'importe quelle distrib)
def get_linux_distro() :
    try : 
        with open("/etc/os-release") as f :
            for line in f :
                if line.startswith("ID=") : 
                    return line.split("=")[1].strip().strip('"')
    except FileNotFoundError : 
        pass
    return None

# Installation Linux
def run_agent_install_linux(server: str, tag: str) :
    cmd = [
        "sudo", "perl", AGENT_LINUX_NAME,
        "-s", server, 
        "-t", tag,
        "--full-inventory-postpone",
        "--install",
        "--runnow",
    ] 
    if DEBUG :
        cmd.append("--debug")
    try : 
        subprocess.run(cmd, check = True)
        log("GLPI Agent installé avec succès.", False)
        return True 
    except subprocess.CalledProcessError as e :
        log(f"Echec de l'installation : {e}")
        return False
    
def cleanup() :
    if os.path.exists(AGENT_LINUX_NAME) : 
        os.remove(AGENT_LINUX_NAME)
        log(f"Fichier temporaire supprimé : {AGENT_LINUX_NAME}", False)

# --------------------------------------- FONCTIONS PRINCIPALES D'INSTALLATION --------------------------------------------------------

# ------------------------- WINDOWS -----------------

def install_glpi_windows(tag: str) :
#     if not uninstall_package(WINGET_AGENT_NAME) : 
    #     return False
    # if is_winget_installed() : 
    #     custom_args = f"SERVER={SERVER} TAG={tag} FULL-INVENTORY-POSTPONE=0 RUNNOW=1"
    #     return install_with_winget(WINGET_AGENT_NAME, custom_args)
    
    try : 
        if not download_file(AGENT_WINDOWS, AGENT_WINDOWS_PATH) :
            return False
        if not install_msi(AGENT_WINDOWS_PATH, SERVER, tag) :
            return False
    finally : 
        if AGENT_WINDOWS_PATH.exists() : 
            AGENT_WINDOWS_PATH.unlink()
    return True

# ------------------------ MAC --------------------------

def install_glpi_mac(tag: str) : 
    try : 
        if not check_dependencies(MISSING_DEPS, REQUIRED_MAC_DEPS) :
            log("Installation des dépendances...", False)
            if not install_dependencies(MISSING_DEPS) :
                return False
        if not download_file(AGENT_MAC, AGENT_MAC_PKG_PATH) :
            return False
        if not install_package_mac(AGENT_MAC_PKG_PATH) :
            return False
        if not create_config_mac(CONFIG_MAC_PATH, SERVER, tag) :
            return False
        if not start_process_mac(AGENT_MAC_NAME) :
            return False
        if not agent_run_mac(AGENT_MAC_PATH) :
            return False
    finally : 
        if AGENT_MAC_PKG_PATH.exists() : 
            AGENT_MAC_PKG_PATH.unlink()
    return True

# ----------------- LINUX --------------------------------

def install_glpi_linux(server: str, tag: str) : 
    distro = get_linux_distro()
    if distro not in SUPPORTED_LINUX_DISTROS :
        log(f"Distribution non supportée : {distro}. \n Voire les solutions possibles : {DOCUMENTATION_LINUX}")
        sys.exit(1) 
    if not check_dependencies(MISSING_DEPS, REQUIRED_LINUX_DEPS) : 
        log("Installation des dépendances...", False)
        if not install_dependencies(MISSING_DEPS) : 
            sys.exit(1)
    if not download_file(AGENT_LINUX) : 
        sys.exit(1)
    if not run_agent_install_linux(server, tag) : 
        sys.exit(1)
    cleanup()

#Télécharger l'Agent Monitor (uniquement disponible pour Windows)
def install_glpi_monitor():
    if not uninstall_package(WINGET_MONITOR_NAME) : 
        return False
    try :
        if not download_file(MONITOR, MONITOR_WINDOWS_PATH) : 
            return False
    except Exception : 
        return False

def main():
    tag = input ("Tag : ")
    if not tag : 
        log("Le tag ne peut pas être vide.")
        sys.exit(1)
    system = platform.system()
    if system == "Windows":
        if not install_glpi_windows(tag) : 
           sys.exit(1)
        if not install_glpi_monitor() :
           sys.exit(1)
    elif system == "Linux":
        if not install_glpi_linux(SERVER, tag) : 
            sys.exit(1)
    elif system == "Darwin":
        if not install_glpi_mac(tag) :
            sys.exit(1)
    else:
        print(f"OS non supporté : {system}")

if __name__ == "__main__":
    main()
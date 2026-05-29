import os
import platform
import subprocess
import sys
import urllib.request


DOCUMENTATION = "https://glpi-agent.readthedocs.io/en/latest/installation/index.html#gnu-linux"
SERVER = "https://micronov.fr36.glpi-network.cloud"
AGENT_LINUX_URL ="https://github.com/glpi-project/glpi-agent/releases/download/1.17/glpi-agent-1.17-linux-installer.pl"
DEBUG = True
SUPPORTED_DISTROS = ["redhat", "centos", "debian", "ubuntu"]

REQUIRED_DEPS = ["perl", "libxml-libxml-perl", "libnet-ip-perl", "dmidecode"]
MISSING_DEPS = []
AGENT_SCRIPT = "glpi-agent-installer.pl"


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
            stdout = subprocess.PIPE if not DEBUG else None,
        )
        log("Dépendances installées avec succès", False)
        return True
    except subprocess.CalledProcessError as e : 
        log(f"Echec de l'installation des dépendances : {e}", True)
        return False

def download_agent() : 
    try : 
        urllib.request.urlretrieve(AGENT_LINUX_URL, AGENT_SCRIPT)
        log(f"Script téléchargé : {AGENT_SCRIPT}", False)
        return True
    except Exception as e :
        log(f"Echec du téléchargement : {e}", True)
        return False
    

def run_agent_install(server, tag) :
    cmd = [
        "sudo", "perl", AGENT_SCRIPT,
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
        log(f"Echec de l'installation : {e}", True)
        return False
    
def cleanup() :
    if os.path.exists(AGENT_SCRIPT) : 
        os.remove(AGENT_SCRIPT)
        log(f"Fichier temporaire supprimé : {AGENT_SCRIPT}", False)


def get_linux_distro() :
    try : 
        with open("/etc/os-release") as f :
            for line in f :
                if line.startswith("ID=") : 
                    return line.split("=")[1].strip().strip('"')
    except FileNotFoundError : 
        pass
    return None

def install_glpi_linux(server, tag) : 
    distro = get_linux_distro()
    if distro not in SUPPORTED_DISTROS :
        log(f"Distribution non supportée : {distro}. \n Voire les solutions possibles : {DOCUMENTATION}", True)
        sys.exit(1) 
    if not check_dependencies() : 
        log("Installation des dépendances...", False)
        if not install_dependencies() : 
            sys.exit(1)
    if not download_agent() : 
        sys.exit(1)
    if not run_agent_install(server, tag) : 
        sys.exit(1)
    cleanup()







def main():
    tag = input ("Tag : ")
    if not tag : 
        log("Le tag ne peut pas être vide.", True)
        sys.exit(1)
    system = platform.system()
    if system == "Linux" :
        install_glpi_linux(SERVER, tag)
    else : 
        log(f"OS non supporté : {system}", True)
        sys.exit(1)


if __name__ == "__main__" : 
    main()
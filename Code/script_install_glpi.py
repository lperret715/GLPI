import os
import platform
import subprocess
import requests

server = "https://micronov.fr36.glpi-network.cloud"
monitor="https://github.com/glpi-project/glpi-agentmonitor/releases/download/1.5.0/GLPI-AgentMonitor-x64.exe"
agent_windows="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17-x64.msi"
agent_mac="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
agent_linux="https://github.com/glpi-project/glpi-agent/releases/download/1.17/glpi-agent-1.17-linux-installer.pl"
Path=os.path.join(os.path.expanduser("~"), "Desktop", "GLPI-Agent.msi")
Monitor_Path=os.path.join(os.path.expanduser("~"), "Desktop", "GLPI-Agent-Monitor.exe")
debug =1
tag = input ("Tag : ")


#Regarder si winget existe
def is_winget_installed():
    try:
        subprocess.run(["winget", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

#Regarder si l'agent existe déjà
def is_glpi_installed():
    try:
        res = subprocess.run(["winget", "list"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "GLPI Agent" in res.stdout
    except Exception:
        return False

#Désinstaller l'agent s'il existe (UNIQUEMENT POUR TESTS, A NE PAS CONSERVER DANS LE CODE FINAL)
def uninstall_glpi_windows():
    if not is_glpi_installed():
        print("GLPI Agent n'est pas installé.")
        return True

    try:
        # Utilise une liste pour éviter les problèmes de guillemets
        cmd = [
            "winget", "uninstall", "GLPI Agent",
            "-e", "--accept-source-agreements"
        ]
        subprocess.run(cmd, check=True, shell=True)
        print("✅ GLPI Agent désinstallé avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur pendant la désinstallation : {e}")
        return False



#Installation Windows
def install_glpi_windows() :
    if not uninstall_glpi_windows(): 
        print("Impossible de désinstaller l'agent existant, installation annulée")
        return
    
    # Si winget non installé, on passe par la voie longue
    if not is_winget_installed():
        print("winget n'est pas installé. Installation classique (plus long)")


        command = [
            f"Invoke-WebRequest -Uri {agent_windows} -Outfile {Path}",
            f"Start-Process msiexec.exe -ArgumentList '/i \"{Path}\" /qb SERVER={server} TAG={tag} RUNNOW=1' -Wait"
           
        ]
        try:
            for cmd in command :
                subprocess.run(
            ["powershell.exe", "-Command", cmd],
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            print(f"✅ Commande exécutée : {cmd}")
            print("✅ Installation terminée avec succès.")
            os.remove(Path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur pendant l'installation : {e}")

        return

    
    commands = [
        f'winget install glpi-agent --custom="SERVER={server} TAG={tag} RUNNOW=1"'
    ]
        

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("✅ GLPI Agent installé avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur pendant l'installation de GLPI Agent : {e}")
        

def install_glpi_agentmonitor():
    commands = [
        f'Invoke-WebRequest -Uri {monitor} -Outfile {Monitor_Path}'
    ]
    
    try:
        for cmd in commands :
            subprocess.run(
                ["powershell.exe", "-Command", cmd],
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
                )
            print(f"✅ Commande exécutée : {cmd}")
            print("✅ Installation terminée avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur pendant l'installation de GLPI Agent-Monitor : {e}")


def main():
    system = platform.system()
    # if system == "Linux":
    #     install_glpi_linux()
    # elif system == "Darwin":
    #     install_glpi_macos()
    if system == "Windows":
       install_glpi_windows()
       install_glpi_agentmonitor()
    else:
        print(f"OS non supporté : {system}")

if __name__ == "__main__":
    main()
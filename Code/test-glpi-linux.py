import os
import platform
import subprocess
import requests

server = "https://micronov.fr36.glpi-network.cloud"
agent_linux="https://github.com/glpi-project/glpi-agent/releases/download/1.17/glpi-agent-1.17-linux-installer.pl"
debug = 1
tag = input ("Tag : ")



def install_glpi_linux() :
    commands = [
        f'sudo apt install {agent_linux} && sudo perl {os.path.basename(agent_linux)} -s {server} -t {tag} -debug --service --install --runnow',
        
    ]
    commands_2 = [
        f'sudo apt update && sudo apt install -y perl libxml-libxml-perl libnet-ip-perl dmidecode'
    ]
        

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("✅ GLPI Agent installé avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur pendant l'installation de GLPI Agent : {e} \n Installation des dépendances : ")
            for cmd in commands_2 : 
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    print("✅ Dépendances installées avec succès.")
                except subprocess.CalledProcessError as e2 :
                    print(f"❌ Erreur pendant l'installation de GLPI Agent : {e} \n Erreur install dépendances : {e2}")




def main():
    system = platform.system()
    if system == "Linux" :
        install_glpi_linux()
    else : 
        print (f"OS non supporté : {system}")


if __name__ == "__main__" : 
    main()
import os
import platform
import subprocess

server="https://micronov.fr36.glpi-network.cloud"
agent_mac="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"

path_config = "/Applications/GLPI-Agent/etc/conf.d/glpi.cfg"
tag = input("Tag : ")

fichier_config = f"""
server = {server}
debug=1
tag={tag}
"""

def install_glpi_mac() : 
    command_install = [
        "cd Desktop",
        f"curl -L -O {agent_mac}"
        f"sudo installer -verbose -pkg $HOME/Desktop/{} -target /Applications"
    ]
    try : 
        for cmd in command_install : 
            subprocess.run(
                cmd,
                check = True,
                shell = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text = True
            )
            print(f"Commande exécutée avec succès : {cmd}")

    except subprocess.CalledProcessError as e :
        print(f"Erreur lors de l'installation : {e}")
    os.makedirs(os.path.dirname(path_config), exist_ok=True)
    with open(path_config, "w") as config_file :
        config_file.write(fichier_config)
    print(f"Fichier créé : {path_config}")
    command_start = [
        "sudo launchctl startorg.glpi-project.glpi-agent"
        "sudo /Applications/GLPI-Agent/bin/glpi-agent"
    ]
    try : 
        for cmd in command_start : 
            subprocess.run(
                cmd,
                check = True,
                shell = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text = True
            )
            print(f"Commande exécutée avec succès : {cmd}")
        print("✅ Installation terminée avec succès.")
    except subprocess.CalledProcessError as e :
        print(f"Erreur lors de l'installation : {e}")

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




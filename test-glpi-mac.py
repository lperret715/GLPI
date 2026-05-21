import os
import platform
import subprocess

server="https://micronov.fr36.glpi-network.cloud"
agent_mac="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
path_desktop = Path=os.path.join(os.path.expanduser("~"), "Desktop")
path_config = "/Applications/GLPI-Agent/etc/conf.d/glpi.cfg"
tag = input("Tag : ")

fichier_config = f"""
server = {server}
debug=1
tag={tag}
"""

def install_glpi_mac() : 
    command_install = f"cd {path_desktop} && curl -L -O {agent_mac} && installer -verbose -pkg {path_desktop}/{os.path.basename(agent_mac)} -target /Applications"
    command_start = [
        "launchctl start org.glpi-project.glpi-agent",
        "/Applications/GLPI-Agent/bin/glpi-agent"
    ]      
    try : 
        subprocess.run(
            command_install,
            check = True,
            shell = True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text = True
            )
        print(f"Commande exécutée avec succès : {command_install}")

    except subprocess.CalledProcessError as e :
        print(f"Erreur lors de l'installation : {e}")
        return
    os.makedirs(os.path.dirname(path_config), exist_ok=True)
    with open(path_config, "w") as config_file :
        config_file.write(fichier_config)
    print(f"Fichier créé : {path_config}")
    

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




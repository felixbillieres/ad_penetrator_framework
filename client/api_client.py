# api_client.py
# Module client pour interagir avec l'API REST du serveur C2.
# Abstraie les requ�tes HTTP (GET, POST) pour les diff�rentes ressources
# (agents, tasks, results, ad_objects).
# Utilise la biblioth�que 'requests'.

import requests

class APIClient:
    def __init__(self, c2_base_url):
        """
        Initialise le client API avec l'URL de base du serveur C2.
        Exemple: http://localhost:8000
        """
        if not c2_base_url.startswith("http://") and not c2_base_url.startswith("https://"):
            raise ValueError("L'URL de base du C2 doit commencer par http:// ou https://")
        self.c2_base_url = c2_base_url.rstrip('/') # S'assurer qu'il n'y a pas de / à la fin

    def get_agents(self):
        """Récupère la liste des agents enregistrés auprès du serveur C2."""
        agents_url = f"{self.c2_base_url}/agents" # Supposant que le serveur a un endpoint /agents
        try:
            response = requests.get(agents_url, timeout=5)
            response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
            return response.json() # Retourne la liste des agents parsée depuis le JSON
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des agents : {e}")
            return [] # Retourne une liste vide en cas d'erreur
        except ValueError as e: # Erreur de parsing JSON
            print(f"Erreur de parsing JSON lors de la récupération des agents : {e}")
            print(f"Réponse brute du serveur : {response.text if 'response' in locals() else 'N/A'}")
            return []

    def check_server_status(self):
        """Vérifie si le serveur C2 est accessible."""
        # Nous pourrions utiliser un endpoint dédié comme /status ou /ping, 
        # ou simplement essayer d'accéder à un endpoint connu comme /agents.
        # Pour l'instant, utilisons /agents pour la simplicité.
        try:
            response = requests.get(f"{self.c2_base_url}/agents", timeout=3)
            # On pourrait vérifier un code de statut spécifique si /agents est protégé
            # Ici, on suppose que si on obtient une réponse sans exception, c'est OK.
            return True, "Connecté au serveur C2."
        except requests.exceptions.Timeout:
            return False, "Timeout : Le serveur C2 n'a pas répondu."
        except requests.exceptions.ConnectionError:
            return False, "Erreur de connexion : Impossible de joindre le serveur C2."
        except requests.exceptions.RequestException as e:
            return False, f"Erreur C2 : {e}"

# Exemple d'utilisation (pourrait être dans gui_main.py plus tard)
if __name__ == '__main__':
    # Ceci est un exemple, l'URL devrait être configurable
    C2_URL = "http://localhost:8000" 
    client = APIClient(c2_base_url=C2_URL)

    print(f"Vérification du statut du serveur C2 ({C2_URL})...")
    status, message = client.check_server_status()
    print(f"Statut : {message}")

    if status:
        print("\nRécupération de la liste des agents...")
        agents = client.get_agents()
        if agents:
            print(f"Agents trouvés ({len(agents)}):")
            for agent in agents:
                print(f"  - ID: {agent.get('id', 'N/A')}, Statut: {agent.get('status', 'N/A')}, Dernier check-in: {agent.get('last_checkin_time', 'N/A')}")
        else:
            print("Aucun agent trouvé ou erreur lors de la récupération.")

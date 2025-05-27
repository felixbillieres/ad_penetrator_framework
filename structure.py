import os

def create_directory_structure(base_path):
    """
    Crée l'arborescence des dossiers et des fichiers pour le projet AD Penetrator Framework.
    Chaque fichier est créé avec une description commentée à son début.
    """
    print(f"Création de la structure du projet à: {os.path.abspath(base_path)}\n")

    structure = {
        "ad_penetrator_framework": {
            "client": {
                "__init__.py": "# Initialisation du package client.\n",
                "console.py": """# console.py
# Point d'entrée de l'interface console interactive pour l'opérateur.
# Gère la logique de l'interface utilisateur, l'affichage des données,
# et l'envoi des commandes au serveur C2 via api_client.py.
# Utilise des bibliothèques comme 'cmd' ou 'prompt_toolkit' pour une meilleure UX.
""",
                "api_client.py": """# api_client.py
# Module client pour interagir avec l'API REST du serveur C2.
# Abstraie les requêtes HTTP (GET, POST) pour les différentes ressources
# (agents, tasks, results, ad_objects).
# Utilise la bibliothèque 'requests'.
""",
                "command_parser.py": """# command_parser.py
# Interprète les commandes saisies par l'opérateur dans la console.
# Traduit les commandes textuelles en appels de fonctions ou en requêtes API
# vers le serveur.
""",
                "reporter_console.py": """# reporter_console.py
# Module responsable de l'affichage des résultats et des données dans la console de l'opérateur.
# Formate les informations récupérées de la base de données du serveur pour une lecture aisée.
# Peut inclure des options de verbosité et de filtrage.
""",
                "playbooks": {
                    "__init__.py": "# Initialisation du package playbooks.\n",
                    "initial_recon.yaml": """# playbooks/initial_recon.yaml
# Exemple de playbook YAML pour une phase de reconnaissance initiale.
# Définit une séquence d'exécution de modules d'énumération sur les agents.
# Peut inclure des conditions et des options d'interactivité.
""",
                    "privilege_escalation.yaml": """# playbooks/privilege_escalation.yaml
# Exemple de playbook YAML pour la phase d'élévation de privilèges.
# Chaîne des modules de découverte de vulnérabilités et propose des exploitations.
# Met en évidence l'interactivité pour l'opérateur.
""",
                }
            },
            "server": {
                "__init__.py": "# Initialisation du package server.\n",
                "app.py": """# app.py
# Point d'entrée principal de l'API web du serveur C2.
# Construit avec un framework web (ex: FastAPI ou Flask) pour gérer les routes
# et les endpoints de communication avec les agents et le client opérateur.
# Gère l'authentification et l'autorisation des requêtes.
""",
                "database.py": """# database.py
# Module pour la configuration et la gestion de la connexion à la base de données.
# Utilise un ORM (ex: SQLAlchemy) pour interagir avec la base de données
# (PostgreSQL, SQLite, etc.).
""",
                "models.py": """# models.py
# Définit les modèles de données de la base de données (avec l'ORM).
# Inclut les modèles pour les agents, les tâches, les résultats, et surtout
# les objets Active Directory découverts (utilisateurs, groupes, ordinateurs, GPOs, trusts, etc.).
""",
                "agent_manager.py": """# agent_manager.py
# Gère l'enregistrement, l'état (online/offline), la version et la configuration des agents connectés.
# Tient à jour la liste des agents et leurs métadonnées.
""",
                "task_queue.py": """# task_queue.py
# Gère une file d'attente pour les tâches à distribuer aux agents.
# Permet de planifier, prioriser et assigner les tâches de manière asynchrone.
""",
                "handlers": {
                    "__init__.py": "# Initialisation du package handlers.\n",
                    "agent_checkin.py": """# handlers/agent_checkin.py
# Gère les requêtes 'check-in' des agents.
# Met à jour le statut de l'agent et lui attribue de nouvelles tâches si disponibles.
""",
                    "task_results.py": """# handlers/task_results.py
# Gère la réception des résultats des tâches exécutées par les agents.
# Valide les données reçues, les stocke dans la base de données
# et peut déclencher des événements ou des analyses post-exécution.
""",
                }
            },
            "agent": {
                "__init__.py": "# Initialisation du package agent.\n",
                "agent_main.py": """# agent_main.py
# Point d'entrée principal du code de l'agent qui s'exécute sur la machine cible.
# Gère la boucle de communication avec le serveur C2 (check-in, get_task, submit_results).
# Initialise les modules de communication et le module d'exécution des tâches.
""",
                "comms": {
                    "__init__.py": "# Initialisation du package comms (communication).\n",
                    "http_beacon.py": """# comms/http_beacon.py
# Module de communication pour l'agent utilisant le protocole HTTP/HTTPS.
# Simule le trafic web légitime pour la furtivité.
# Gère le 'jitter' et le 'sleep' pour varier les intervalles de communication.
""",
                    "dns_beacon.py": """# comms/dns_beacon.py
# Module de communication pour l'agent utilisant le protocole DNS.
# Exfiltre les données et reçoit les commandes via des requêtes DNS (ex: TXT records).
# Utile pour les réseaux avec des restrictions de sortie.
""",
                    # Possibilité d'ajouter smb_beacon.py, etc.
                },
                "core": {
                    "__init__.py": "# Initialisation du package core (noyau de l'agent).\n",
                    "module_loader.py": """# core/module_loader.py
# Responsable du chargement dynamique des modules Python envoyés par le serveur C2.
# Permet à l'agent d'exécuter des fonctionnalités spécifiques sans les avoir toutes embarquées par défaut.
""",
                    "task_executor.py": """# core/task_executor.py
# Exécute les tâches reçues du serveur C2.
# Prend les commandes, les associe aux modules chargés et gère leur exécution.
# Capture les sorties et les erreurs pour les renvoyer au serveur.
""",
                    "local_datastore.py": """# core/local_datastore.py
# Un cache optionnel pour les données Active Directory que l'agent a déjà énumérées localement.
# Peut éviter des requêtes réseau répétées vers le serveur pour des données fréquemment consultées.
""",
                    "environment_check.py": """# core/environment_check.py
# Effectue des vérifications sur l'environnement d'exécution de l'agent.
# Détecte l'OS, les privilèges locaux, la présence d'outils de sécurité (AV/EDR),
# et d'environnements virtualisés.
""",
                },
                "modules": {
                    "__init__.py": "# Initialisation du package modules de l'agent.\n",
                    "base_agent_module.py": """# modules/base_agent_module.py
# Classe abstraite ou interface de base pour tous les modules d'énumération et d'exploitation de l'agent.
# Définit une interface commune (méthode 'execute', propriétés 'name', 'description').
""",
                    "ad": {
                        "__init__.py": "# Initialisation du package ad (interactions AD de l'agent).\n",
                        "ldap_client.py": """# ad/ldap_client.py
# Fonctions de bas niveau pour les interactions LDAP avec Active Directory.
# Adapté pour l'exécution sur l'agent (potentiellement minimisé/optimisé).
# Utilise des bibliothèques comme 'ldap3'.
""",
                        "impacket_wrapper.py": """# ad/impacket_wrapper.py
# Un wrapper pour les fonctions sélectionnées de la bibliothèque Impacket.
# Permet à l'agent d'utiliser des capacités d'exploitation réseau avancées (SMB, RPC, Kerberos).
""",
                        "wmi_client.py": """# ad/wmi_client.py
# Fonctions pour interagir avec WMI (Windows Management Instrumentation) sur la cible.
# Utilisé pour l'énumération locale et l'exécution de commandes.
""",
                    },
                    "enumeration": {
                        "__init__.py": "# Initialisation du package enumeration de l'agent.\n",
                        "users_groups.py": """# enumeration/users_groups.py
# Module pour énumérer les utilisateurs, les groupes et leurs attributs via LDAP.
# Collecte des informations pertinentes pour la phase de reconnaissance.
""",
                        "trusts.py": """# enumeration/trusts.py
# Module pour énumérer les trusts (relations d'approbation) entre domaines Active Directory.
# Identifie la directionnalité, la quarantaine SID et les chemins potentiels de pivot.
""",
                        "adcs.py": """# enumeration/adcs.py
# Module pour énumérer les Autorités de Certification (CA) et les templates de certificats ADCS.
# Collecte les ACLs et les configurations des templates pour identifier les vulnérabilités ESC.
""",
                        "acl_scanner.py": """# enumeration/acl_scanner.py
# Module pour scanner et analyser les listes de contrôle d'accès (ACLs) sur des objets AD critiques.
# Recherche des permissions abusives (ex: droits WriteDACL, WriteProperty) sur les objets du domaine.
""",
                        "gpos.py": """# enumeration/gpos.py
# Module pour énumérer les objets de stratégie de groupe (GPO) et leurs permissions.
# Recherche des GPO non liées, ou des GPO modifiables par des utilisateurs non-admin.
""",
                        "spns.py": """# enumeration/spns.py
# Module pour énumérer les Service Principal Names (SPNs) enregistrés dans l'AD.
# Utilisé pour identifier les comptes de service potentiellement vulnérables au Kerberoasting.
""",
                    },
                    "exploitation": {
                        "__init__.py": "# Initialisation du package exploitation de l'agent.\n",
                        "kerberoast.py": """# exploitation/kerberoast.py
# Module pour l'exploitation de Kerberoasting.
# Tente de demander des tickets de service (TGS) pour les SPNs énumérés et de cracker les hashes.
""",
                        "esc8.py": """# exploitation/esc8.py
# Module pour l'exploitation de la vulnérabilité ESC8 (Shadow Credentials) via la modification de msDS-KeyCredentialLink.
# Nécessite des droits d'écriture spécifiques sur un objet utilisateur ou ordinateur.
""",
                        "password_spray.py": """# exploitation/password_spray.py
# Module pour effectuer des attaques de pulvérisation de mots de passe (Password Spraying).
# Tente d'authentifier une liste de mots de passe faibles sur de nombreux comptes utilisateurs.
""",
                        "golden_ticket.py": """# exploitation/golden_ticket.py
# Module pour la création et l'injection d'un Golden Ticket Kerberos.
# Nécessite les privilèges Domain Admin pour récupérer le hash du compte krbtgt.
""",
                        "dcsync.py": """# exploitation/dcsync.py
# Module pour effectuer une attaque DCSync.
# Tente de récupérer les hashes de tous les utilisateurs du domaine à partir d'un contrôleur de domaine.
# Nécessite des droits spécifiques (ex: DC Replication) sur l'objet Domain.
""",
                        "trust_abuse.py": """# exploitation/trust_abuse.py
# Module pour l'abus de trusts Active Directory.
# Peut inclure la création de tickets Kerberos pour des domaines liés ou l'exploitation de délégations inter-domaines.
""",
                        "lateral_movement": {
                            "__init__.py": "# Initialisation du package lateral_movement (mouvement latéral).\n",
                            "pth_ptt.py": """# lateral_movement/pth_ptt.py
# Module pour les techniques Pass-the-Hash (PtH) et Pass-the-Ticket (PtT).
# Permet de s'authentifier sur d'autres machines sans avoir le mot de passe en clair.
""",
                            "wmi_exec.py": """# lateral_movement/wmi_exec.py
# Module pour l'exécution de commandes à distance via WMI.
# Utilise des informations d'identification obtenues pour se déplacer latéralement.
""",
                            "smb_exec.py": """# lateral_movement/smb_exec.py
# Module pour l'exécution de commandes à distance via SMB (ex: PsExec-like).
""",
                        },
                    },
                    "utils": {
                        "__init__.py": "# Initialisation du package utils de l'agent.\n",
                        "powershell_exec.py": """# utils/powershell_exec.py
# Fonctions utilitaires pour exécuter des commandes PowerShell sur la machine cible.
# Peut inclure des techniques d'obfuscation et de contournement d'AMSI.
""",
                        "bypasses.py": """# utils/bypasses.py
# Fonctions pour contourner les mécanismes de sécurité Windows (UAC, AMSI, AppLocker).
# Utilisé pour l'exécution furtive de code.
""",
                        "memory_patching.py": """# utils/memory_patching.py
# Fonctions pour modifier la mémoire de processus existants.
# Peut être utilisé pour désactiver la journalisation ou les hooks d'outils de sécurité.
""",
                    },
                }
            },
            "shared": {
                "__init__.py": "# Initialisation du package shared (code partagé).\n",
                "constants.py": """# constants.py
# Définit les constantes partagées entre le client, le serveur et l'agent.
# Inclut les types de modules, les codes de statut des tâches, les niveaux de journalisation.
""",
                "data_models.py": """# data_models.py
# Définit les modèles de données structurés (avec Pydantic) pour la communication.
# Assure la validation et la cohérence des données échangées (tâches, résultats, objets AD).
""",
                "exceptions.py": """# exceptions.py
# Définit les classes d'exceptions personnalisées utilisées à travers le framework.
# Améliore la gestion des erreurs et la lisibilité du code.
""",
                "serialisation.py": """# serialisation.py
# Fonctions utilitaires pour la sérialisation et la désérialisation des données.
# Gère la conversion des objets Python en formats transportables (JSON) et vice-versa.
""",
            },
            "tools": {
                "__init__.py": "# Initialisation du package tools.\n",
                "build_agent.py": """# tools/build_agent.py
# Script pour construire et packager l'agent (ex: avec PyInstaller pour un exécutable).
# Permet de générer différentes versions de l'agent (Python script, standalone EXE).
""",
                "obfuscate_agent.py": """# tools/obfuscate_agent.py
# Script pour obfuscater le code source de l'agent.
# Utilise des techniques comme l'encodage, le renommage de variables, pour compliquer l'analyse.
""",
                "generate_stager.py": """# tools/generate_stager.py
# Script pour générer un 'stager' (petit script ou commande) pour le premier contact avec la cible.
# Le stager est responsable du téléchargement et de l'exécution de l'agent complet.
# Peut générer des stagers PowerShell, CMD, VBScript, etc.
""",
            },
            "README.md": "", # Le contenu du README sera ajouté après la création de la structure.
        }
    }

    def create_files_and_dirs(current_path, structure_dict):
        for name, content in structure_dict.items():
            path = os.path.join(current_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                print(f"Création du dossier: {path}")
                create_files_and_dirs(path, content)
            else:
                with open(path, "w") as f:
                    f.write(content)
                print(f"Création du fichier: {path}")

    create_files_and_dirs(base_path, structure)
    print("\nStructure du projet créée avec succès.")

if __name__ == "__main__":
    base_dir = "ad_penetrator_framework"
    create_directory_structure(base_dir)

    # Ajout du contenu du README.md une fois la structure créée
    readme_content = """
# AD Penetrator Framework

## Introduction

Le **AD Penetrator Framework** est une suite d'outils avancée et hautement modulaire conçue pour la reconnaissance, l'énumération, la détection de vulnérabilités et l'exploitation au sein des environnements Active Directory. Inspiré des frameworks de C2 (Command & Control), il offre une architecture distribuée avec un serveur central, un client opérateur interactif et des agents légers et furtifs déployés sur les systèmes cibles.

Ce framework vise à automatiser et à orchestrer des chaînes d'attaques complexes, allant des techniques classiques d'énumération LDAP aux abus de protocole avancés, en passant par l'exploitation de misconfigurations Active Directory et le mouvement latéral. Il est conçu pour être **ultra-scalable**, permettant l'ajout facile de nouvelles techniques et la personnalisation de playbooks pour des scénarios de test d'intrusion spécifiques.

## Architecture

Le framework est bâti sur une architecture **Client-Serveur-Agent (C2)**, favorisant la modularité, l'évolutivité et la flexibilité d'exécution.
+-------------------+       +-------------------+       +--------------------+
|                   |       |                   |       |                    |
|      Client       |<----->|       Server      |<----->|       Agent(s)     |
|   (Operator PC)   |       |    (C2 Server)    |       |   (Target Hosts)   |
|                   |       |                   |       |                    |
+-------------------+       +-------------------+       +--------------------+
Console CLI                API / Database            Executes Modules
Playbook Orchestration     Task Management           Collects Data
Result Display             Agent Control             Performs Exploits
Stores AD Data            Communicates back
"""
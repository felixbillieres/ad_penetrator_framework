# app.py
# Point d'entrée principal de l'API web du serveur C2.
# Construit avec un framework web (ex: FastAPI ou Flask) pour gérer les routes
# et les endpoints de communication avec les agents et le client opérateur.
# Gére l'authentification et l'autorisation des requêtes.

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse # Ajout pour la réponse HTML
from sqlalchemy.orm import Session
from typing import List, Optional # Ajout de Optional
from pydantic import BaseModel, Field
import datetime

from fastapi.middleware.cors import CORSMiddleware # Ajout pour CORS

from . import models, database # Nouvelle importation relative
from .models import AgentStatus # Nouvelle importation relative

# Créer les tables dans la base de données au démarrage (si elles n'existent pas)
# database.create_db_and_tables() # SUPPRIMÉ: L'appel global est supprimé

# NOUVEAU: Fonction pour l'événement de démarrage
async def startup_event():
    print("APP: Événement de démarrage FastAPI déclenché.")
    database.create_db_and_tables()
    print("APP: create_db_and_tables appelée depuis l'événement de démarrage.")

app = FastAPI(
    title="AD Penetrator Framework - C2 Server",
    description="API pour le serveur C2 du AD Penetrator Framework. Accédez à /docs ou /redoc pour la documentation interactive de l'API.",
    version="0.1.0",
    docs_url="/docs", # URL explicite pour Swagger UI
    redoc_url="/redoc",  # URL explicite pour ReDoc
    on_startup=[startup_event] # AJOUTÉ: Enregistrement de l'événement de démarrage
)

# Configuration CORS
# Pour le développement, nous autorisons toutes les origines ("*").
# Pour la production, vous devriez restreindre cela à l'URL de votre frontend.
origins = [
    "*", # Permet toutes les origines, y compris file:// (null) et localhost sur divers ports
    # Exemple plus restrictif pour la production :
    # "http://votre-domaine-frontend.com",
    # "https://votre-domaine-frontend.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"], # Autorise tous les headers
)

# --- Page d'accueil simple ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
        <head>
            <title>AD Penetrator Framework - C2 Server</title>
            <style>
                body { font-family: sans-serif; margin: 40px; background-color: #f0f0f0; color: #333; }
                h1 { color: #1a237e; }
                p { font-size: 1.1em; }
                a { color: #1a237e; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AD Penetrator Framework - C2 Server</h1>
                <p>Le serveur C2 est opérationnel.</p>
                <p>Ceci est une API RESTful conçue pour être utilisée par le client graphique AD Penetrator.</p>
                <p>
                    Pour explorer les endpoints de l'API, veuillez visiter:
                    <ul>
                        <li><a href="/docs">/docs</a> (Swagger UI)</li>
                        <li><a href="/redoc">/redoc</a> (ReDoc)</li>
                    </ul>
                </p>
            </div>
        </body>
    </html>
    """

# --- Pydantic Models for Request/Response --- 
class AgentCheckInRequest(BaseModel):
    agent_id: str = Field(..., description="Unique ID de l'agent")
    hostname: Optional[str] = Field(None, description="Nom d'hôte de la machine agent")
    internal_ip: Optional[str] = Field(None, description="Adresse IP interne de l'agent")
    username: Optional[str] = Field(None, description="Utilisateur sous lequel l'agent s'exécute")
    os_target: Optional[str] = Field(None, description="OS de la machine agent")
    agent_version: Optional[str] = Field(None, description="Version du binaire de l'agent")
    
    # Nouveaux champs pour informations système détaillées
    architecture: Optional[str] = Field(None, description="Architecture de la machine (ex: x86_64)")
    processor: Optional[str] = Field(None, description="Informations sur le processeur")
    current_user: Optional[str] = Field(None, description="Utilisateur actuellement connecté qui exécute l'agent")
    domain_name: Optional[str] = Field(None, description="Nom de domaine AD (si joint)")
    local_users: Optional[List[str]] = Field(None, description="Liste des utilisateurs locaux découverts")
    local_admins: Optional[List[str]] = Field(None, description="Liste des membres du groupe Administrateurs local")
    current_user_privileges: Optional[str] = Field(None, description="Privilèges de l'utilisateur de l'agent (Admin/User)")

class AgentResponse(BaseModel):
    id: str
    hostname: Optional[str] = None
    internal_ip: Optional[str] = None
    username: Optional[str] = None
    os_target: Optional[str] = None
    status: AgentStatus
    first_seen: datetime.datetime
    last_checkin_time: Optional[datetime.datetime] = None
    agent_version: Optional[str] = None

    # Nouveaux champs correspondants pour la réponse
    architecture: Optional[str] = None
    processor: Optional[str] = None
    current_user: Optional[str] = None
    domain_name: Optional[str] = None
    local_users: Optional[List[str]] = None
    local_admins: Optional[List[str]] = None
    current_user_privileges: Optional[str] = None

    class Config:
        # orm_mode = True # Ancien nom pour Pydantic V1
        from_attributes = True # Nouveau nom pour Pydantic V2+

# --- API Endpoints --- 

@app.post("/agent/checkin", response_model=AgentResponse, summary="Permet à un agent de s'enregistrer ou de signaler sa présence.")
def agent_checkin(agent_data: AgentCheckInRequest, db: Session = Depends(database.get_db)):
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_data.agent_id).first()
    current_time = datetime.datetime.now(datetime.timezone.utc)

    if db_agent:
        # Agent existant, mettre à jour les informations
        db_agent.last_checkin_time = current_time
        db_agent.status = AgentStatus.ACTIVE
        if agent_data.hostname: db_agent.hostname = agent_data.hostname
        if agent_data.internal_ip: db_agent.internal_ip = agent_data.internal_ip
        if agent_data.os_target: db_agent.os_target = agent_data.os_target
        if agent_data.agent_version: db_agent.agent_version = agent_data.agent_version

        # Mise à jour des nouveaux champs
        if agent_data.architecture: db_agent.architecture = agent_data.architecture
        if agent_data.processor: db_agent.processor = agent_data.processor
        if agent_data.current_user: db_agent.username = agent_data.current_user
        if agent_data.domain_name: db_agent.domain_name = agent_data.domain_name
        if agent_data.local_users is not None: db_agent.local_users = agent_data.local_users
        if agent_data.local_admins is not None: db_agent.local_admins = agent_data.local_admins
        if agent_data.current_user_privileges: db_agent.current_user_privileges = agent_data.current_user_privileges
    else:
        # Nouvel agent
        db_agent = models.Agent(
            id=agent_data.agent_id,
            hostname=agent_data.hostname,
            internal_ip=agent_data.internal_ip,
            username=agent_data.current_user,
            os_target=agent_data.os_target,
            agent_version=agent_data.agent_version,
            status=AgentStatus.ACTIVE,
            first_seen=current_time,
            last_checkin_time=current_time,
            
            # Nouveaux champs
            architecture=agent_data.architecture,
            processor=agent_data.processor,
            domain_name=agent_data.domain_name,
            local_users=agent_data.local_users,
            local_admins=agent_data.local_admins,
            current_user_privileges=agent_data.current_user_privileges
        )
        db.add(db_agent)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/agents", response_model=List[AgentResponse], summary="Récupère la liste de tous les agents enregistrés.")
def get_all_agents(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    agents = db.query(models.Agent).offset(skip).limit(limit).all()
    return agents

@app.get("/agents/{agent_id}", response_model=AgentResponse, summary="Récupère les détails d'un agent spécifique.")
def get_agent_details(agent_id: str, db: Session = Depends(database.get_db)):
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return db_agent

# Point d'entrée pour uvicorn si on exécute `python server/app.py`
if __name__ == "__main__":
    import uvicorn
    from server.config import C2_HOST, C2_PORT # Importer depuis la config

    print(f"Démarrage du serveur C2 sur {C2_HOST}:{C2_PORT}")
    print(f"Base de données utilisée : {database.DATABASE_URL}")
    print("Tables créées si elles n'existaient pas.")
    
    uvicorn.run(app, host=C2_HOST, port=C2_PORT, log_level="info", reload=True) # Note: uvicorn.run attend "module:variable"

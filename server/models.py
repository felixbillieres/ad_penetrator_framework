# models.py
# Définit les modèles de données de la base de données (avec l'ORM).
# Inclut les modèles pour les agents, les tâches, les résultats, et surtout
# les objets Active Directory découverts (utilisateurs, groupes, ordinateurs, GPOs, trusts, etc.).

from sqlalchemy import Column, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    UNINSTALLED = "uninstalled"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True) # UUID de l'agent
    hostname = Column(String, nullable=True)
    internal_ip = Column(String, nullable=True)
    username = Column(String, nullable=True)
    os_target = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(AgentStatus), default=AgentStatus.PENDING)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_checkin_time = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    agent_version = Column(String, nullable=True)

    def __repr__(self):
        return f"<Agent(id='{self.id}', status='{self.status}', last_checkin='{self.last_checkin_time}')>"

# Plus tard, nous ajouterons d'autres modèles ici pour :
# - Tâches (Tasks)
# - Résultats des tâches (TaskResults)
# - Objets AD (ADObjects : utilisateurs, groupes, ordinateurs, GPOs, etc.)
# - Credentials
# - Logs d'événements

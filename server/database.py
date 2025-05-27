# database.py
# Module pour la configuration et la gestion de la connexion à la base de données.
# Utilise un ORM (ex: SQLAlchemy) pour interagir avec la base de données
# (PostgreSQL, SQLite, etc.).

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from server.config import DATABASE_URL # Importer depuis la configuration
from server.models import Base # Importer la Base depuis models.py pour créer les tables

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Nécessaire pour SQLite avec FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour créer les tables dans la base de données
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# Dépendance pour obtenir une session de base de données par requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

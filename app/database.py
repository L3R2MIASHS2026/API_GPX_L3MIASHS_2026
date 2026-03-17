from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de données SQLite locale
# Le fichier trails.db sera créé automatiquement à la racine de ton projet
SQLALCHEMY_DATABASE_URL = "sqlite:///./app/trails.db"
# Création du moteur SQLite
# L'argument check_same_thread=False est spécifique à SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Usine à sessions pour interagir avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tes modèles (Trail, TrailPoint)
Base = declarative_base()
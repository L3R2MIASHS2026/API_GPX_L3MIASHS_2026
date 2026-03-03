import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. On cherche une variable d'environnement (fournie par Render)
# Sinon, on utilise ta base SQLite locale par défaut
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trails.db")


if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. Configuration du moteur selon la base utilisée
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Configuration spécifique pour SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Configuration standard pour PostgreSQL (Render)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
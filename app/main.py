import glob
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.exc import SQLAlchemyError

from app.routes import router
from app.db_connection import engine, Base, SessionLocal
from app.api_schemas import TrailSchema
from app.db_models import Trail, TrailPoint
from app.trail_service import TrailService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création des tables
Base.metadata.create_all(bind=engine)


def load_initial_data() -> None:
    """
    Charge les fichiers GPX présents dans le dossier `data/` au démarrage de l'application.
    Ignore l'importation si la base de données contient déjà des traces.
    """
    db = SessionLocal()
    service = TrailService(db)

    traces_existantes = service.get_all_trails()
    if traces_existantes:
        logger.info("La base de données contient déjà des traces. Importation des GPX ignorée.")
        db.close()
        return


    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")

    if not os.path.exists(data_dir):
        logger.warning(f"Le dossier {data_dir} n'existe pas.")
        db.close()
        return

    gpx_files = glob.glob(os.path.join(data_dir, "*.gpx"))
    if not gpx_files:
        logger.info("Aucun fichier GPX trouvé dans le dossier data.")
        db.close()
        return

    logger.info("Base de données vide : début de l'importation des fichiers GPX...")

    try:
        for file_path in gpx_files:
            file_name = os.path.basename(file_path)
            logger.info(f"Traitement du fichier : {file_name}")

            # Vérification de l'existence du trail (au cas où)
            existing = service.get_trail_by_name(file_name)
            if existing:
                logger.info(f"Le fichier {file_name} est déjà chargé.")
                continue

            # Lecture et validation du fichier
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        logger.warning(f"Le fichier {file_name} est vide.")
                        continue
            except IOError as e:
                logger.error(f"Erreur de lecture du fichier {file_name}: {e}")
                continue

            # Création du trail
            trail_create = TrailSchema(
                name=file_name,
                gpx_content=content
            )

            try:
                service.create_trail(trail_create)
                logger.info(f"Fichier {file_name} importé avec succès.")
            except SQLAlchemyError as e:
                logger.error(f"Erreur lors de l'import du fichier {file_name}: {e}")
                db.rollback()

    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement des données initiales: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie pour charger les données initiales au démarrage."""
    # La fonction se lancera à chaque fois, mais s'arrêtera
    # toute seule si la base est déjà pleine
    load_initial_data()
    yield
    logger.info("Arrêt de l'application.")

app = FastAPI(
    title="Trails API",
    description="API de recherche de traces de trail à partir de fichiers GPX",
    version="1.0.0",
    lifespan=lifespan,
    servers=[
        {"url": "https://api-gpx-l3miashs-2026.onrender.com", "description": "Serveur Render (Production)"},
        {"url": "http://127.0.0.1:8000", "description": "Serveur Local (Développement)"}
    ]
)

# Configuration du CORS pour autoriser GitHub Pages à interroger l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
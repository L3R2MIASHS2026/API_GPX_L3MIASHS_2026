import glob
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.controller import router
from app.database import engine, Base, SessionLocal
from app.models import TrailSchema, Trail, TrailPoint
from app.services import TrailService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création des tables
Base.metadata.create_all(bind=engine)


def load_initial_data() -> None:
    """
    Charge les fichiers GPX présents dans le dossier `data/` au démarrage de l'application.
    Ignore les fichiers déjà présents en base de données.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")

    if not os.path.exists(data_dir):
        logger.warning(f"Le dossier {data_dir} n'existe pas.")
        return

    gpx_files = glob.glob(os.path.join(data_dir, "*.gpx"))
    if not gpx_files:
        logger.info("Aucun fichier GPX trouvé dans le dossier data.")
        return

    db = SessionLocal()
    service = TrailService(db)

    try:
        for file_path in gpx_files:
            file_name = os.path.basename(file_path)
            logger.info(f"Traitement du fichier : {file_name}")

            # Vérification de l'existence du trail
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
                description=f"Importé automatiquement depuis {file_name}",
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
    load_initial_data()
    yield
    logger.info("Arrêt de l'application.")


app = FastAPI(
    title="Trails API",
    description="API de recherche de traces de trail à partir de fichiers GPX",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

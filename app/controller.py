from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

# --- Imports locaux ---
from app.database import SessionLocal
from app.models import TrailSchema
from app.services import TrailService
from app.folium_integration import generate_trail_map

# On enlève le tag global ici pour pouvoir les définir précisément sur chaque route
router = APIRouter()

ERROR_TRAIL_NOT_FOUND = "Trace non trouvée"


# --- Dépendances ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)) -> TrailService:
    return TrailService(db)


# --- Routes : GESTION DES TRACES ---

@router.get(
    "/traces",
    response_model=List[TrailSchema],
    summary="Lister les traces",
    tags=["Gestion des Traces"],
    responses={200: {"description": "Liste des traces récupérée avec succès"}},
)
def get_traces(
        service: Annotated[TrailService, Depends(get_service)],
        min_dist: Annotated[float, Query(description="Distance min (km)")] = 0,
        max_dist: Annotated[float, Query(description="Distance max (km)")] = float('inf'),
):
    return service.get_trails_by_distance(min_dist, max_dist)


@router.get(
    "/traces/{trail_id}",
    response_model=TrailSchema,
    summary="Obtenir une trace",
    tags=["Gestion des Traces"],
    responses={404: {"description": ERROR_TRAIL_NOT_FOUND}},
)
def get_trace(
        trail_id: int,
        service: Annotated[TrailService, Depends(get_service)],
):
    if not (trail := service.get_trail(trail_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TRAIL_NOT_FOUND)
    return trail


@router.post(
    "/traces",
    response_model=TrailSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une trace",
    tags=["Gestion des Traces"],
    responses={201: {"description": "Trace créée avec succès"}},
)
def create_trace(
        trail: TrailSchema,
        service: Annotated[TrailService, Depends(get_service)],
):
    return service.create_trail(trail)


@router.put(
    "/traces/{trail_id}",
    response_model=TrailSchema,
    summary="Mettre à jour une trace",
    tags=["Gestion des Traces"],
    responses={404: {"description": ERROR_TRAIL_NOT_FOUND}},
)
def update_trace(
        trail_id: int,
        trail: TrailSchema,
        service: Annotated[TrailService, Depends(get_service)],
):
    if not (updated_trail := service.update_trail(trail_id, trail)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TRAIL_NOT_FOUND)
    return updated_trail


@router.delete(
    "/traces/{trail_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une trace",
    tags=["Gestion des Traces"],
    responses={404: {"description": ERROR_TRAIL_NOT_FOUND}},
)
def delete_trace(
        trail_id: int,
        service: Annotated[TrailService, Depends(get_service)],
):
    if not service.delete_trail(trail_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TRAIL_NOT_FOUND)


# --- Routes : CARTOGRAPHIE (HTML) ---

@router.get(
    "/traces/{trail_id}/carte",
    response_class=HTMLResponse,
    summary="Afficher la carte d'une trace",
    tags=["Cartographie"]
)
def get_trail_map(
        trail_id: int,
        service: Annotated[TrailService, Depends(get_service)]
):
    trail = service.get_trail(trail_id)
    if not trail:
        raise HTTPException(status_code=404, detail=ERROR_TRAIL_NOT_FOUND)

    map_html = generate_trail_map(trail)
    return HTMLResponse(content=map_html)
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import SessionLocal
from models import TrailSchema
from services import TrailService

from fastapi.responses import HTMLResponse
from folium_integration import map_traces

router = APIRouter(tags=["Traces"])

ERROR_TRAIL_NOT_FOUND = "Trace non trouvée"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)) -> TrailService:
    return TrailService(db)


@router.get(
    "/traces",
    response_model=List[TrailSchema],
    summary="Lister les traces",
    responses={200: {"description": "Liste des traces récupérée avec succès"}},
)
def get_traces(
        service: Annotated[TrailService, Depends(get_service)],
        min_dist: Annotated[float, Query(description="Distance min (km)")] = 0,
        max_dist: Annotated[float, Query(description="Distance max (km)")] = float('inf'),
):
    trails_by_distance = service.get_trails_by_distance(min_dist, max_dist)
    return HTMLResponse(content=map_traces(trails_by_distance))


@router.get(
    "/traces/{trail_id}",
    response_model=TrailSchema,
    summary="Obtenir une trace",
    responses={404: {"description": ERROR_TRAIL_NOT_FOUND}},
)
def get_trace(
        trail_id: int,
        service: Annotated[TrailService, Depends(get_service)],
):
    if not (trail := service.get_trail(trail_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TRAIL_NOT_FOUND)
    html_map = map_traces(trail)
    return HTMLResponse(content=html_map)

@router.get(
    "/traces/map", 
    response_class=HTMLResponse, # on dit à FastAPI de renvoyer du HTML
    summary="Afficher la carte de toutes les traces"
)
def get_traces_map(service: Annotated[TrailService, Depends(get_service)]):
    # On récupère toutes les traces de la base de données
    all_trails = service.get_trails_by_distance(min_dist, max_dist)
     # On génère le code HTML de la carte folium
    html_map = map_traces(all_trails)
    # On renvoie la page web
    return HTMLResponse(content=html_map)

@router.post(
    "/traces",
    response_model=TrailSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une trace",
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
    responses={404: {"description": ERROR_TRAIL_NOT_FOUND}},
)
def delete_trace(
        trail_id: int,
        service: Annotated[TrailService, Depends(get_service)],
):
    if not service.delete_trail(trail_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TRAIL_NOT_FOUND)

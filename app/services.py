import logging
from typing import Optional, List, Dict, Any, Tuple

import gpxpy
from gpxpy.gpx import GPXTrackPoint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Trail, TrailSchema, TrailPoint

logger = logging.getLogger(__name__)


class GPXParser:
    @staticmethod
    def parse_gpx(gpx_content: str) -> Tuple[Dict[str, Any], List[GPXTrackPoint]]:
        """
        Parse le contenu GPX et retourne les métadonnées et la liste des points.
        """
        if not gpx_content.strip():
            raise ValueError("Le contenu GPX est vide.")

        try:
            gpx = gpxpy.parse(gpx_content)
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing du GPX : {e}")

        # Si le fichier ne contient aucune trace, on renvoie des zéros
        if not gpx.tracks:
            meta = {
                "length": 0.0,
                "elevation_gain": 0.0,
                "elevation_loss": 0.0,
                "altitude_max": 0.0,
                "altitude_min": 0.0,
                "start_location": None
            }
            points = []

        # CALCULS de gpxpy
        else:
            moving_data = gpx.get_moving_data()
            uphill, downhill = gpx.get_uphill_downhill()
            min_alt, max_alt = gpx.get_elevation_extremes()

            # Récupération du premier point pour la localisation de départ
            start_loc = None
            first_track = gpx.tracks[0]
            if first_track.segments and first_track.segments[0].points:
                pt = first_track.segments[0].points[0]
                start_loc = f"{pt.latitude}, {pt.longitude}"

            # On range tous nos calculs dans un petit dictionnaire propre
            meta = {
                "length": round(moving_data.moving_distance / 1000, 2) if moving_data else 0.0,
                "elevation_gain": round(uphill, 2),
                "elevation_loss": round(downhill, 2),
                "altitude_max": round(max_alt, 2),
                "altitude_min": round(min_alt, 2),
                "start_location": start_loc
            }

            # On extrait tous les points GPS
            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    points.extend(segment.points)

        return meta, points


class TrailService:
    def __init__(self, db: Session):
        self.db = db

    def create_trail(self, trail_create: TrailSchema) -> Trail:
        """Crée une nouvelle trace avec ses points à partir des données fournies."""
        trail_dict = trail_create.model_dump(exclude_unset=True)
        # On retire les points vides du dictionnaire pour ne pas perturber SQLAlchemy
        trail_dict.pop("points", None)

        points_to_add = []

        if trail_create.gpx_content:
            try:
                meta, gpx_points = GPXParser.parse_gpx(trail_create.gpx_content)

                for key, value in meta.items():
                    if trail_dict.get(key) is None and value is not None:
                        trail_dict[key] = round(value, 2) if isinstance(value, float) else value

                for idx, pt in enumerate(gpx_points):
                    points_to_add.append(TrailPoint(
                        latitude=pt.latitude,
                        longitude=pt.longitude,
                        altitude=pt.elevation,
                        order=idx
                    ))

            except Exception as e:
                logger.warning(f"Échec du parsing GPX: {e}")

        new_trail = Trail(**trail_dict)

        if points_to_add:
            new_trail.points = points_to_add

        self.db.add(new_trail)
        try:
            self.db.commit()
            self.db.refresh(new_trail)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur lors de la création de la trace: {e}")
            raise
        return new_trail

    def get_all_trails(self) -> List[Trail]:
        """Récupère toutes les traces."""
        return self.db.query(Trail).all()

    def get_trail(self, trail_id: int) -> Optional[Trail]:
        """Récupère une trace par son identifiant."""
        return self.db.query(Trail).filter(Trail.id == trail_id).first()

    def get_trail_by_name(self, name: str) -> Optional[Trail]:
        """Récupère une trace par son nom."""
        return self.db.query(Trail).filter(Trail.name == name).first()

    def get_trails_by_distance(self, min_dist: float, max_dist: float) -> List[Trail]:
        """Récupère les traces dont la longueur est comprise entre min_dist et max_dist."""
        return self.db.query(Trail).filter(
            Trail.length >= min_dist,
            Trail.length <= max_dist
        ).all()

    def update_trail(self, trail_id: int, trail_data: TrailSchema) -> Optional[Trail]:
        """Met à jour une trace existante."""
        trail = self.db.query(Trail).filter(Trail.id == trail_id).first()
        if not trail:
            return None

        for key, value in trail_data.model_dump(exclude_unset=True).items():
            if key not in ["gpx_content", "points", "id"]:
                setattr(trail, key, value)

        if trail_data.gpx_content:
            trail.gpx_content = trail_data.gpx_content

        try:
            self.db.commit()
            self.db.refresh(trail)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur lors de la mise à jour de la trace: {e}")
            raise
        return trail

    def delete_trail(self, trail_id: int) -> bool:
        """Supprime une trace par son identifiant."""
        trail = self.db.query(Trail).filter(Trail.id == trail_id).first()
        if not trail:
            return False
        self.db.delete(trail)
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur lors de la suppression de la trace: {e}")
            raise
        return True

    
    def get_trail_points(trail: Trail, step=1):
        """Récupère les points pour l'affichage Folium."""
        _, points = GPXParser.parse_gpx(trail.gpx_content)
        liste_lonlat = [[pts.latitude, pts.longitude] for pts in points]
        if step > 1:
            return liste_lonlat[::step]
        else:
            return liste_lonlat
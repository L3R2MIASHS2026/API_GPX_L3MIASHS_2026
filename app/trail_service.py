import logging
from typing import Optional, List, Dict, Any, Tuple

import gpxpy
from gpxpy.gpx import GPXTrackPoint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_models import Trail, TrailPoint
from app.api_schemas import TrailSchema

logger = logging.getLogger(__name__)


class GPXParser:
    @staticmethod
    def parse_gpx(gpx_content: str) -> Tuple[Dict[str, Any], List[GPXTrackPoint]]:
        """Parse le contenu GPX et retourne les métadonnées et la liste des points."""
        if not gpx_content.strip():
            raise ValueError("Le contenu GPX est vide.")

        try:
            gpx = gpxpy.parse(gpx_content)
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing du GPX : {e}")

        # Si le fichier ne contient ni traces ni routes, on renvoie des zéros
        if not gpx.tracks and not gpx.routes:
            meta = {
                "length": 0.0,
                "elevation_gain": 0.0,
                "elevation_loss": 0.0,
                "altitude_max": 0.0,
                "altitude_min": 0.0,
                "start_location": None
            }
            return meta, []


        distance_meters = gpx.length_3d() if gpx.has_elevations() else gpx.length_2d()

        uphill, downhill = gpx.get_uphill_downhill()
        min_alt, max_alt = gpx.get_elevation_extremes()

        # Récupération du premier point (Traces puis Routes)
        start_lat = None
        start_lon = None

        if gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points:
            pt = gpx.tracks[0].segments[0].points[0]
            start_lat = pt.latitude
            start_lon = pt.longitude
        elif gpx.routes and gpx.routes[0].points:
            pt = gpx.routes[0].points[0]
            start_lat = pt.latitude
            start_lon = pt.longitude

        meta = {
            "length": round(distance_meters / 1000, 2),
            "elevation_gain": round(uphill, 2) if uphill else 0.0,
            "elevation_loss": round(downhill, 2) if downhill else 0.0,
            "altitude_max": round(max_alt, 2) if max_alt else 0.0,
            "altitude_min": round(min_alt, 2) if min_alt else 0.0,
            # On stocke les floats avec 5 décimales (précision d'environ 1 mètre)
            "start_latitude": round(start_lat, 5) if start_lat is not None else None,
            "start_longitude": round(start_lon, 5) if start_lon is not None else None
        }

        # On extrait tous les points GPS (Traces ET Routes)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                points.extend(segment.points)

        for route in gpx.routes:
            points.extend(route.points)

        return meta, points


class TrailService:
    def __init__(self, db: Session):
        self.db = db

    def create_trail(self, trail_create: TrailSchema) -> Trail:
        """Crée une nouvelle trace avec ses points à partir des données fournies."""
        # On transforme le schéma en dictionnaire classique
        trail_dict = trail_create.model_dump(exclude_unset=True)

        trail_dict.pop("points", None)
        # On extrait gpx_content pour l'utiliser en calcul, puis on le retire du dict
        gpx_content_temp = trail_dict.pop("gpx_content", None)
        trail_dict.pop("description", None)  # On retire aussi la description par sécurité

        points_to_add = []

        if gpx_content_temp:
            try:
                # On utilise gpx_content_temp pour faire les calculs
                meta, gpx_points = GPXParser.parse_gpx(gpx_content_temp)

                for key, value in meta.items():
                    if trail_dict.get(key) is None and value is not None:
                        trail_dict[key] = round(value, 2) if isinstance(value, float) else value

                for idx, pt in enumerate(gpx_points):
                    points_to_add.append(TrailPoint(
                        latitude=pt.latitude,
                        longitude=pt.longitude,
                        altitude=pt.elevation if hasattr(pt, 'elevation') else None,
                        order=idx
                    ))

            except Exception as e:
                logger.warning(f"Échec du parsing GPX: {e}")

        # Ici, trail_dict est "propre", il n'a plus de gpx_content
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

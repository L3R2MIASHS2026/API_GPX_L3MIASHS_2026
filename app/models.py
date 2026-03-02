import datetime
from typing import Optional
# Pydantic sert à valider les données qui entrent et sortent de l'API
from pydantic import BaseModel, Field, field_validator
# SQLAlchemy sert à construire les tables dans la base de données
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func

from database import Base


# --- SQLAlchemy Models ---

class Trail(Base):
    __tablename__ = "trails"

    # Impossible d'avoir deux traces avec le même nom
    __table_args__ = (UniqueConstraint("name", name="uq_trail_name"),)

    # Définition des colonnes
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    gpx_content = Column(Text, nullable=True)
    length = Column(Float, nullable=True)
    elevation_gain = Column(Float, nullable=True)
    elevation_loss = Column(Float, nullable=True)
    start_location = Column(String, nullable=True)
    altitude_max = Column(Float, nullable=True)
    altitude_min = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# --- Pydantic Models ---

class TrailSchema(BaseModel):
    # Field(...) permet de donner des exemples qui s'afficheront dans la doc de l'API
    id: Optional[int] = Field(None, example=1)
    name: str = Field(..., example="Ma Trace de Randonnée")
    description: Optional[str] = Field(None, example="Une belle randonnée en montagne")
    gpx_content: Optional[str] = Field(None, example="<gpx>...</gpx>")

    # ge=0 signifie doit être positif ou nul
    length: Optional[float] = Field(None, example=10.5, ge=0)
    elevation_gain: Optional[float] = Field(None, example=500.0, ge=0)
    elevation_loss: Optional[float] = Field(None, example=500.0, ge=0)
    start_location: Optional[str] = Field(None, example="45.0, 5.0")
    altitude_max: Optional[float] = Field(None, example=2000.0, ge=0)
    altitude_min: Optional[float] = Field(None, example=1000.0, ge=0)
    created_at: Optional[datetime.datetime] = Field(None, example="2023-01-01T12:00:00Z")

    # Cette configuration permet à Pydantic de lire directement 
    # les objets SQLAlchemy (notre classe Trail au-dessus)
    model_config = {
        "from_attributes": True,
    }

    @field_validator("length", "elevation_gain", "elevation_loss", "altitude_max", "altitude_min")
    def check_positive_values(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("La valeur doit être positive")
        return value #Redondans, méthode de classe qui peut servir a autre chose. Ex : vérifier que l'altitude max est sup a l'altitude min

import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class TrailPointSchema(BaseModel):
    id: Optional[int] = Field(None)
    trail_id: int
    latitude: float
    longitude: float
    altitude: Optional[float] = Field(None)
    order: int

    model_config = {
        "from_attributes": True,
    }


class TrailSchema(BaseModel):
    id: Optional[int] = Field(None, example=1)
    name: str = Field(..., example="Ma Trace de Randonnée")
    description: Optional[str] = Field(None, example="Une belle randonnée en montagne")
    gpx_content: Optional[str] = Field(None, example="<gpx>...</gpx>")
    length: Optional[float] = Field(None, example=10.5, ge=0)
    elevation_gain: Optional[float] = Field(None, example=500.0, ge=0)
    elevation_loss: Optional[float] = Field(None, example=500.0, ge=0)
    start_location: Optional[str] = Field(None, example="45.0, 5.0")
    altitude_max: Optional[float] = Field(None, example=2000.0)
    altitude_min: Optional[float] = Field(None, example=1000.0)
    created_at: Optional[datetime.datetime] = Field(None, example="2023-01-01T12:00:00Z")

    points: List[TrailPointSchema] = []

    model_config = {
        "from_attributes": True,
    }

    @field_validator("length", "elevation_gain", "elevation_loss")
    def check_positive_values(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("La valeur doit être positive")
        return value

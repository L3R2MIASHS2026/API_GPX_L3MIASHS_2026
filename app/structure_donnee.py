
# SQLAlchemy sert à construire les tables dans la base de données
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


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

    points = relationship("TrailPoint", back_populates="trail", cascade="all, delete-orphan")

class TrailPoint(Base):

    __tablename__ = "trail_points"

    id = Column(Integer, primary_key=True, index=True)
    trail_id = Column(Integer, ForeignKey("trails.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    order = Column(Integer, nullable=False)

    trail = relationship("Trail", back_populates="points")

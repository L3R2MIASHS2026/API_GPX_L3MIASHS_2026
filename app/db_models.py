from sqlalchemy import Column, Integer, String, Float, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.db_connection import Base


class Trail(Base):
    __tablename__ = "trails"

    __table_args__ = (
        UniqueConstraint("name", name="uq_trail_name"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)

    # Colonnes pour les calculs géographiques
    length = Column(Float, index=True, nullable=True)
    elevation_gain = Column(Float, index=True, nullable=True)
    elevation_loss = Column(Float, nullable=True)
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    altitude_max = Column(Float, nullable=True)
    altitude_min = Column(Float, nullable=True)

    points = relationship("TrailPoint", back_populates="trail", cascade="all, delete-orphan")


class TrailPoint(Base):
    __tablename__ = "trail_points"

    __table_args__ = (
        UniqueConstraint("trail_id", "order", name="uq_trail_point_order"),
    )

    id = Column(Integer, primary_key=True)
    trail_id = Column(Integer, ForeignKey("trails.id"), index=True, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    order = Column(Integer, nullable=False)

    trail = relationship("Trail", back_populates="points")
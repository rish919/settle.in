from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CityDB(Base):
    __tablename__ = "cities"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    state = Column(String)
    country = Column(String, default="India")
    population = Column(Integer, nullable=True)
    lat = Column(Float)
    lng = Column(Float)

    # Relationship to LocalityDB
    localities = relationship("LocalityDB", back_populates="city", cascade="all, delete-orphan")


class LocalityDB(Base):
    __tablename__ = "localities"

    id = Column(String, primary_key=True, index=True)
    city_id = Column(String, ForeignKey("cities.id"))
    name = Column(String, index=True)
    lat = Column(Float)
    lng = Column(Float)

    safety_score = Column(Float, nullable=True)
    air_quality_index = Column(Integer, nullable=True)
    avg_rent = Column(Integer, nullable=True)
    commute_score = Column(Float, nullable=True)
    cost_of_living_index = Column(Float, nullable=True)
    healthcare_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)

    city = relationship("CityDB", back_populates="localities")
    amenities = relationship("AmenityDB", back_populates="locality", cascade="all, delete-orphan")


class AmenityDB(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    locality_id = Column(String, ForeignKey("localities.id"))
    category = Column(String, index=True) # e.g. 'hospitals', 'schools', 'parks', 'supermarkets'
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)

    locality = relationship("LocalityDB", back_populates="amenities")

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
    historical_data = relationship("HistoricalDataDB", back_populates="locality", cascade="all, delete-orphan", order_by="HistoricalDataDB.month_year")


class HistoricalDataDB(Base):
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    locality_id = Column(String, ForeignKey("localities.id"))
    month_year = Column(String, index=True) # format: "YYYY-MM"
    rent = Column(Integer, nullable=True)
    aqi = Column(Integer, nullable=True)
    crime_rate = Column(Float, nullable=True)

    locality = relationship("LocalityDB", back_populates="historical_data")


class AmenityDB(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    locality_id = Column(String, ForeignKey("localities.id"))
    category = Column(String, index=True) # e.g. 'hospitals', 'schools', 'parks', 'supermarkets'
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)

    locality = relationship("LocalityDB", back_populates="amenities")

class UserInteractionDB(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, index=True) # Anonymous session ID or user ID
    locality_id = Column(String, ForeignKey("localities.id"))
    interaction_type = Column(String) # 'like', 'dislike', 'save', 'too_expensive', 'too_far'
    timestamp = Column(String) # ISO format timestamp
    
    # We store the context in which the interaction was made to use for ML later
    context_budget = Column(Integer, nullable=True)
    context_commute_weight = Column(Float, nullable=True)
    
    locality = relationship("LocalityDB")


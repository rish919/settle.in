"""
settle — City & Neighborhood Pydantic Models

These models define the data shapes for API responses.
When a database is added later, SQLAlchemy models will live
alongside these (or in a separate db_models.py file).
"""

from pydantic import BaseModel
from typing import Optional


class HistoricalData(BaseModel):
    """Represents historical time-series data for a locality."""
    month_year: str
    rent: Optional[int] = None
    aqi: Optional[int] = None
    crime_rate: Optional[float] = None


class Locality(BaseModel):
    """Represents a specific neighborhood/locality within a city."""

    id: str
    name: str
    lat: float
    lng: float
    city_id: Optional[str] = None
    city_name: Optional[str] = None

    # Livability metrics
    safety_score: Optional[float] = None
    air_quality_index: Optional[int] = None
    avg_rent: Optional[int] = None
    commute_score: Optional[float] = None
    cost_of_living_index: Optional[float] = None
    healthcare_score: Optional[float] = None
    education_score: Optional[float] = None
    nearby_services: Optional[dict] = None


class City(BaseModel):
    """Represents a city with its key livability metrics."""

    id: str
    name: str
    state: str
    country: str = "India"
    population: Optional[int] = None
    lat: float
    lng: float

    # Livability metrics (scores are 1–10 scale unless noted)
    safety_score: Optional[float] = None
    air_quality_index: Optional[int] = None      # AQI value (lower is better)
    avg_rent: Optional[int] = None                # Monthly rent in local currency
    commute_score: Optional[float] = None
    cost_of_living_index: Optional[float] = None
    healthcare_score: Optional[float] = None
    education_score: Optional[float] = None

    # job_market_score, nightlife_score, green_space_score, etc.

    localities: list[Locality] = []


class CityListResponse(BaseModel):
    """Response wrapper for a list of cities."""

    count: int
    cities: list[City]

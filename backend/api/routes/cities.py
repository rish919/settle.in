"""
settle — City Routes

API endpoints for retrieving city and neighborhood data.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from services import city_service
from models.city import CityListResponse
from database import get_db

router = APIRouter()


@router.get("/cities", response_model=CityListResponse)
def list_cities(
    search: Optional[str] = None,
    max_rent: Optional[int] = None,
    min_safety: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of cities, with optional filters.
    """
    cities = city_service.get_all_cities(
        db=db,
        search=search,
        max_rent=max_rent,
        min_safety=min_safety,
    )
    return CityListResponse(count=len(cities), cities=cities)


@router.get("/cities/{city_id}")
def get_city(city_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a single city.
    """
    city = city_service.get_city_by_id(db, city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")
    return city


@router.get("/cities/{city_id}/localities/{locality_id}")
def get_locality(city_id: str, locality_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a single locality within a city.
    """
    locality = city_service.get_locality_by_id(db, city_id, locality_id)
    if not locality:
        raise HTTPException(status_code=404, detail=f"Locality '{locality_id}' not found in city '{city_id}'")
    return locality


@router.get("/compare")
def compare_locations(
    type: str = Query(..., description="Type of comparison: 'city' or 'locality'"),
    id1: str = Query(..., description="ID of first location"),
    id2: str = Query(..., description="ID of second location"),
    city_id1: Optional[str] = Query(None, description="City ID for first locality (required if type='locality')"),
    city_id2: Optional[str] = Query(None, description="City ID for second locality (required if type='locality')"),
    db: Session = Depends(get_db)
):
    """
    Compare two cities or two localities.
    """
    if type == "city":
        loc1 = city_service.get_city_by_id(db, id1)
        loc2 = city_service.get_city_by_id(db, id2)
        if not loc1 or not loc2:
            raise HTTPException(status_code=404, detail="One or both cities not found")
        return {"location1": loc1, "location2": loc2}
        
    elif type == "locality":
        if not city_id1 or not city_id2:
            raise HTTPException(status_code=400, detail="city_id1 and city_id2 are required for locality comparison")
        loc1 = city_service.get_locality_by_id(db, city_id1, id1)
        loc2 = city_service.get_locality_by_id(db, city_id2, id2)
        if not loc1 or not loc2:
            raise HTTPException(status_code=404, detail="One or both localities not found")
        return {"location1": loc1, "location2": loc2}
        
    else:
        raise HTTPException(status_code=400, detail="Invalid comparison type. Use 'city' or 'locality'")

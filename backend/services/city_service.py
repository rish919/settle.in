"""
settle — City Service

Business logic for city data operations.
Now uses PostgreSQL (via SQLAlchemy) instead of mock data.
"""

from typing import Optional
from sqlalchemy.orm import Session
from models.db_models import CityDB, LocalityDB, AmenityDB, HistoricalDataDB
from models.city import City, Locality, HistoricalData


def get_all_cities(
    db: Session,
    search: Optional[str] = None,
    max_rent: Optional[int] = None,
    min_safety: Optional[float] = None,
) -> list[City]:
    """
    Return a list of cities. Filters for max_rent and min_safety
    were previously used on mock aggregates, but now we return all cities matching the search.
    """
    query = db.query(CityDB)
    
    if search:
        query = query.filter(CityDB.name.ilike(f"%{search}%"))
        
    cities_db = query.all()
    
    # We can just return the DB objects directly because Pydantic v2's from_attributes=True 
    # (or parsing from dict) handles ORM objects if configured. But to be safe and match 
    # the existing `City` model (which might not have from_attributes=True), we instantiate them.
    # Actually, the router returns a Pydantic model which will auto-parse the DB objects 
    # if `from_attributes=True` is set on the model.
    # Let's manually construct them to avoid touching the pydantic model for now.
    results = []
    for c in cities_db:
        # Fetch localities for this city so Compare page can list them
        localities_db = db.query(LocalityDB).filter(LocalityDB.city_id == c.id).all()
        localities = [
            Locality(
                id=loc.id, name=loc.name, lat=loc.lat, lng=loc.lng,
                safety_score=loc.safety_score,
                air_quality_index=loc.air_quality_index,
                avg_rent=loc.avg_rent,
                commute_score=loc.commute_score,
                cost_of_living_index=loc.cost_of_living_index,
                healthcare_score=loc.healthcare_score,
                education_score=loc.education_score,
                city_id=loc.city_id,
                city_name=c.name
            )
            for loc in localities_db
        ]
        results.append(City(
            id=c.id, name=c.name, state=c.state, country=c.country, 
            population=c.population, lat=c.lat, lng=c.lng,
            localities=localities
        ))
    return results


def get_city_by_id(db: Session, city_id: str) -> Optional[City]:
    """
    Return a single city by its ID.
    """
    # Fetch the city and its localities
    city_db = db.query(CityDB).filter(CityDB.id == city_id).first()
    if not city_db:
        return None
        
    # Fetch localities for this city
    localities_db = db.query(LocalityDB).filter(LocalityDB.city_id == city_id).all()
    localities = []
    
    # Calculate city averages from localities
    sum_safety, sum_aqi, sum_rent = 0, 0, 0
    sum_commute, sum_col, sum_health, sum_edu = 0, 0, 0, 0
    count = 0
    
    for loc_db in localities_db:
        localities.append(Locality(
            id=loc_db.id,
            name=loc_db.name,
            lat=loc_db.lat,
            lng=loc_db.lng,
            safety_score=loc_db.safety_score,
            air_quality_index=loc_db.air_quality_index,
            avg_rent=loc_db.avg_rent,
            commute_score=loc_db.commute_score,
            cost_of_living_index=loc_db.cost_of_living_index,
            healthcare_score=loc_db.healthcare_score,
            education_score=loc_db.education_score,
            city_id=city_db.id,
            city_name=city_db.name
        ))
        if loc_db.safety_score and loc_db.avg_rent and loc_db.air_quality_index:
            sum_safety += loc_db.safety_score
            sum_aqi += loc_db.air_quality_index
            sum_rent += loc_db.avg_rent
            if loc_db.commute_score: sum_commute += loc_db.commute_score
            if loc_db.cost_of_living_index: sum_col += loc_db.cost_of_living_index
            if loc_db.healthcare_score: sum_health += loc_db.healthcare_score
            if loc_db.education_score: sum_edu += loc_db.education_score
            count += 1
            
    avg_safety = round(sum_safety / count, 1) if count > 0 else None
    avg_aqi = round(sum_aqi / count) if count > 0 else None
    avg_rent = round(sum_rent / count) if count > 0 else None
    avg_commute = round(sum_commute / count, 1) if count > 0 else None
    avg_col = round(sum_col / count, 1) if count > 0 else None
    avg_health = round(sum_health / count, 1) if count > 0 else None
    avg_edu = round(sum_edu / count, 1) if count > 0 else None

    return City(
        id=city_db.id, name=city_db.name, state=city_db.state, 
        country=city_db.country, population=city_db.population, 
        lat=city_db.lat, lng=city_db.lng,
        safety_score=avg_safety,
        air_quality_index=avg_aqi,
        avg_rent=avg_rent,
        commute_score=avg_commute,
        cost_of_living_index=avg_col,
        healthcare_score=avg_health,
        education_score=avg_edu,
        localities=localities
    )


def get_locality_by_id(db: Session, city_id: str, locality_id: str) -> Optional[Locality]:
    """
    Return a single locality by its ID within a specific city.
    """
    loc_db = db.query(LocalityDB).filter(
        LocalityDB.city_id == city_id,
        LocalityDB.id == locality_id
    ).first()
    
    if not loc_db:
        return None
        
    # Build nearby_services dictionary
    nearby_services = {}
    for amenity in loc_db.amenities:
        if amenity.category not in nearby_services:
            nearby_services[amenity.category] = []
        nearby_services[amenity.category].append({
            "name": amenity.name,
            "lat": amenity.lat,
            "lng": amenity.lng
        })
        
    return Locality(
        id=loc_db.id,
        name=loc_db.name,
        lat=loc_db.lat,
        lng=loc_db.lng,
        safety_score=loc_db.safety_score,
        air_quality_index=loc_db.air_quality_index,
        avg_rent=loc_db.avg_rent,
        commute_score=loc_db.commute_score,
        cost_of_living_index=loc_db.cost_of_living_index,
        healthcare_score=loc_db.healthcare_score,
        education_score=loc_db.education_score,
        nearby_services=nearby_services,
        city_id=city_id,
        city_name=loc_db.city.name if loc_db.city else "Unknown"
    )

def get_locality_history(db: Session, locality_id: str) -> list[HistoricalData]:
    """
    Get 24 months of historical data for a locality, sorted chronologically.
    """
    hist_db = (
        db.query(HistoricalDataDB)
        .filter(HistoricalDataDB.locality_id == locality_id)
        .order_by(HistoricalDataDB.month_year.asc())
        .all()
    )
    
    return [
        HistoricalData(
            month_year=h.month_year,
            rent=h.rent,
            aqi=h.aqi,
            crime_rate=h.crime_rate
        ) for h in hist_db
    ]

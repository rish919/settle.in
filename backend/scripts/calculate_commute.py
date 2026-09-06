"""
settle — Commute Score Calculator

Uses the free OSRM Routing API to calculate the driving time from 
each locality to the city's central business district (CBD) or tech hub,
and converts the duration into a Commute Score (1-10).
"""

import sys
import os
import httpx
import asyncio
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Central Business Districts / Major Tech Hubs for the 8 cities (lat, lng)
CITY_HUBS = {
    "Bangalore": (12.9352, 77.6245),  # Koramangala/ORR Tech Hub
    "Mumbai": (19.0658, 72.8683),     # Bandra Kurla Complex (BKC)
    "Delhi": (28.6304, 77.2177),      # Connaught Place (CP)
    "Hyderabad": (17.4435, 78.3772),  # HITEC City
    "Chennai": (13.0012, 80.2565),    # Guindy / Taramani IT Corridor
    "Pune": (18.5905, 73.7272),       # Hinjewadi IT Park
    "Kolkata": (22.5726, 88.4338),    # Sector V, Salt Lake
    "Ahmedabad": (23.0258, 72.5060)   # SG Highway / Satellite area
}

OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving"

async def fetch_driving_duration(lat1, lng1, lat2, lng2) -> float:
    """Returns driving duration in minutes using OSRM."""
    url = f"{OSRM_API_URL}/{lng1},{lat1};{lng2},{lat2}?overview=false"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                duration_seconds = data["routes"][0]["duration"]
                return duration_seconds / 60.0
    except Exception as e:
        logger.error(f"Failed to fetch routing data: {e}")
    
    # Fallback to straight-line distance approximation (roughly 1km = 3 mins in city traffic)
    from scripts.calculate_safety_scores import haversine
    dist_km = haversine(lat1, lng1, lat2, lng2)
    return dist_km * 3.0

async def calculate_commute_scores():
    db = SessionLocal()
    try:
        cities = db.query(CityDB).all()
        updated_count = 0
        
        for city in cities:
            if city.name not in CITY_HUBS:
                continue
                
            hub_lat, hub_lng = CITY_HUBS[city.name]
            localities = db.query(LocalityDB).filter(LocalityDB.city_id == city.id).all()
            
            for loc in localities:
                duration_mins = await fetch_driving_duration(loc.lat, loc.lng, hub_lat, hub_lng)
                
                # Convert duration to score (1-10)
                # < 15 mins = 9.5
                # 30 mins = 7.0
                # 60 mins = 4.0
                # > 90 mins = 1.0
                if duration_mins <= 15:
                    score = 9.5 - (duration_mins / 15.0) * 0.5
                elif duration_mins <= 60:
                    score = 9.0 - ((duration_mins - 15) / 45.0) * 5.0
                else:
                    score = 4.0 - ((duration_mins - 60) / 60.0) * 3.0
                    
                score = max(1.0, min(10.0, score))
                loc.commute_score = round(score, 1)
                
                logger.info(f"[{city.name}] {loc.name} -> Hub: {round(duration_mins,1)} mins = Score {loc.commute_score}/10")
                updated_count += 1
                
                # Sleep briefly to respect OSRM public API limits
                await asyncio.sleep(0.5)
                
        db.commit()
        logger.info(f"Successfully updated commute scores for {updated_count} localities.")
        
    except Exception as e:
        logger.error(f"Error calculating commute scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(calculate_commute_scores())

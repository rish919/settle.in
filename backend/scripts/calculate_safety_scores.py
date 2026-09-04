"""
settle — Intelligent Safety Score Calculator

Calculates a realistic proxy safety score for each locality based on:
1. Base City Safety Index (Numbeo proxy)
2. Distance from City Center
3. Infrastructure Density (Hospitals, Schools)
4. Economic Proxy (Locality Avg Rent vs City Avg Rent)
"""

import math
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base safety scores (out of 10) for Indian cities based on Numbeo Safety Index
CITY_BASE_SAFETY = {
    "Ahmedabad": 6.8,
    "Pune": 6.5,
    "Hyderabad": 6.3,
    "Bangalore": 6.0,
    "Chennai": 5.9,
    "Mumbai": 5.8,
    "Kolkata": 5.5,
    "Delhi": 4.1
}

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371  # Radius of earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_safety_scores():
    db = SessionLocal()
    try:
        cities = db.query(CityDB).all()
        for city in cities:
            base_score = CITY_BASE_SAFETY.get(city.name, 5.0)
            localities = db.query(LocalityDB).filter(LocalityDB.city_id == city.id).all()
            
            if not localities:
                continue
                
            # Calculate city avg rent to use as an economic proxy
            valid_rents = [l.avg_rent for l in localities if l.avg_rent]
            city_avg_rent = sum(valid_rents) / len(valid_rents) if valid_rents else 25000
            
            for loc in localities:
                modifiers = 0.0
                
                # 1. Distance from Center Modifier
                # Closer to center = slightly more active/lit = +0.5 max. Far = -0.5
                dist_km = haversine(city.lat, city.lng, loc.lat, loc.lng)
                if dist_km < 3:
                    modifiers += 0.5
                elif dist_km > 10:
                    modifiers -= 0.5
                    
                # 2. Infrastructure Density Modifier (Hospitals & Schools)
                hospitals_count = db.query(AmenityDB).filter(
                    AmenityDB.locality_id == loc.id, AmenityDB.category == "hospitals"
                ).count()
                schools_count = db.query(AmenityDB).filter(
                    AmenityDB.locality_id == loc.id, AmenityDB.category == "schools"
                ).count()
                
                # Cap the density bonuses
                hospitals_bonus = min(hospitals_count * 0.15, 1.0)
                schools_bonus = min(schools_count * 0.1, 0.5)
                modifiers += hospitals_bonus + schools_bonus
                
                # 3. Economic Proxy Modifier
                # Higher rent relative to city average often correlates with gated communities / private security
                if loc.avg_rent and loc.avg_rent > city_avg_rent * 1.5:
                    modifiers += 0.8
                elif loc.avg_rent and loc.avg_rent > city_avg_rent * 1.2:
                    modifiers += 0.4
                elif loc.avg_rent and loc.avg_rent < city_avg_rent * 0.7:
                    modifiers -= 0.5
                    
                # Calculate final score and clamp between 1.0 and 10.0
                final_score = base_score + modifiers
                final_score = max(1.0, min(10.0, final_score))
                
                # Update the DB
                loc.safety_score = round(final_score, 1)
                logger.info(f"[{city.name}] {loc.name}: Base {base_score}, Mod {round(modifiers,2)} -> Final {loc.safety_score}/10")
                
        db.commit()
        logger.info("Successfully updated safety scores for all localities.")
        
    except Exception as e:
        logger.error(f"Error calculating safety scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    calculate_safety_scores()

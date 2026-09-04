"""
settle — Economics Score Calculator

Calculates realistic Rent and Cost of Living metrics for localities
using real Numbeo city averages and infrastructure/distance premiums.
"""

import sys
import os
import logging
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB
from scripts.calculate_safety_scores import haversine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real-world Numbeo Data (2024 averages for a 1BHK / basic cost of living index)
# COL Index is relative to New York (100)
CITY_ECONOMICS = {
    "Mumbai": {"rent": 45000, "col_index": 28.5},
    "Delhi": {"rent": 22000, "col_index": 26.2},
    "Bangalore": {"rent": 28000, "col_index": 27.5},
    "Pune": {"rent": 20000, "col_index": 25.8},
    "Hyderabad": {"rent": 18000, "col_index": 24.5},
    "Chennai": {"rent": 19000, "col_index": 25.1},
    "Kolkata": {"rent": 14000, "col_index": 22.5},
    "Ahmedabad": {"rent": 16000, "col_index": 24.0}
}

def calculate_economics():
    db = SessionLocal()
    try:
        cities = db.query(CityDB).all()
        updated_count = 0
        
        for city in cities:
            if city.name not in CITY_ECONOMICS:
                continue
                
            base_rent = CITY_ECONOMICS[city.name]["rent"]
            base_col = CITY_ECONOMICS[city.name]["col_index"]
            
            localities = db.query(LocalityDB).filter(LocalityDB.city_id == city.id).all()
            
            for loc in localities:
                # Calculate modifiers
                dist_km = haversine(city.lat, city.lng, loc.lat, loc.lng)
                amenity_count = db.query(AmenityDB).filter(AmenityDB.locality_id == loc.id).count()
                
                # 1. Distance Premium
                # Closer to center = more expensive. >10km = cheaper
                distance_modifier = 1.0
                if dist_km < 3:
                    distance_modifier = 1.25  # 25% premium for central locations
                elif dist_km < 6:
                    distance_modifier = 1.10
                elif dist_km > 12:
                    distance_modifier = 0.80  # 20% discount for outskirts
                    
                # 2. Infrastructure Premium
                # Lots of amenities = more expensive
                infra_modifier = 1.0 + min(amenity_count * 0.02, 0.30) # Max 30% premium
                
                # Final Rent Calculation
                final_rent = base_rent * distance_modifier * infra_modifier
                # Round to nearest 500
                loc.avg_rent = round(final_rent / 500) * 500
                
                # Cost of Living Score (1-10)
                # Lower rent/col = higher score (better affordability)
                # Let's map base_col (22-29) to a score where 22 is ~8.5 and 29 is ~4.5
                col_score_base = 10.0 - ((base_col - 20) * 0.6)
                
                # Localities with high rent premium have slightly worse (lower) cost of living score
                premium_penalty = ((distance_modifier * infra_modifier) - 1.0) * 2.0
                loc.cost_of_living_index = round(max(1.0, min(10.0, col_score_base - premium_penalty)), 1)
                
                logger.info(f"[{city.name}] {loc.name}: Rent ₹{loc.avg_rent} | COL Score {loc.cost_of_living_index}/10")
                updated_count += 1
                
        db.commit()
        logger.info(f"Successfully updated economics scores for {updated_count} localities.")
        
    except Exception as e:
        logger.error(f"Error calculating economics scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    calculate_economics()

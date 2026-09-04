"""
settle — Infrastructure Score Calculator

Calculates Healthcare and Education scores (1-10) based on real OpenStreetMap data.
"""

import sys
import os
import logging
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import LocalityDB, AmenityDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_infrastructure_scores():
    db = SessionLocal()
    try:
        localities = db.query(LocalityDB).all()
        updated_count = 0
        
        for loc in localities:
            # Count amenities
            hospitals = db.query(AmenityDB).filter(
                AmenityDB.locality_id == loc.id, 
                AmenityDB.category == "hospitals"
            ).count()
            
            schools = db.query(AmenityDB).filter(
                AmenityDB.locality_id == loc.id, 
                AmenityDB.category == "schools"
            ).count()
            
            # Healthcare Score Algorithm
            # 0 hospitals = ~4.0, 1 = ~6.0, 5+ = 9.5+
            health_score = 4.0 + (5.5 * (1 - math.exp(-0.4 * hospitals)))
            health_score = max(1.0, min(10.0, health_score))
            
            # Education Score Algorithm
            # 0 schools = ~4.0, 1 = ~5.0, 8+ = 9.5+
            edu_score = 4.0 + (5.5 * (1 - math.exp(-0.3 * schools)))
            edu_score = max(1.0, min(10.0, edu_score))
            
            loc.healthcare_score = round(health_score, 1)
            loc.education_score = round(edu_score, 1)
            
            logger.info(f"[{loc.name}] Hospitals: {hospitals} -> Health: {loc.healthcare_score} | Schools: {schools} -> Edu: {loc.education_score}")
            updated_count += 1
            
        db.commit()
        logger.info(f"Successfully updated infrastructure scores for {updated_count} localities.")
        
    except Exception as e:
        logger.error(f"Error calculating scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    calculate_infrastructure_scores()

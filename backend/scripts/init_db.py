"""
settle -- Database Initialization Script

Step 1 of the data pipeline:
  1. init_db.py             -> Seeds city names + locality coordinates
  2. fetch_amenities.py     -> Overpass API fetches nearby amenities
  3. trigger_aqi_update.py  -> Open-Meteo fetches real-time AQI
  4. calculate_commute.py   -> OSRM calculates drive-time commute scores
  5. calculate_economics.py -> Numbeo-based rent + cost of living
  6. calculate_safety_scores.py -> Proxy safety from infrastructure + economics
  7. calculate_infrastructure_scores.py -> Healthcare + Education from amenity density
  8. generate_history.py    -> Builds 24-month time-series from computed metrics
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base, SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB, HistoricalDataDB
from data.real_localities import REAL_CITIES


def seed_database():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding database with curated locality data (names + coordinates only)...")
        total_locs = 0
        
        for city_data in REAL_CITIES:
            city_id = city_data["id"]
            locs = city_data.get("localities", [])
            print(f"  [{city_data['name']}] {len(locs)} localities")
            
            city_db = CityDB(
                id=city_id,
                name=city_data["name"],
                state=city_data["state"],
                country=city_data.get("country", "India"),
                population=city_data.get("population"),
                lat=city_data["lat"],
                lng=city_data["lng"]
            )
            db.add(city_db)
            db.flush()
            
            for loc_data in locs:
                loc_db = LocalityDB(
                    id=loc_data["id"],
                    city_id=city_id,
                    name=loc_data["name"],
                    lat=loc_data["lat"],
                    lng=loc_data["lng"],
                    # All metrics left NULL -- computed by the pipeline scripts
                )
                db.add(loc_db)
                total_locs += 1
        
        db.commit()
        print(f"\n Seed complete: {len(REAL_CITIES)} cities, {total_locs} localities.")
        print("    Next: Run the data pipeline to compute metrics.")
        print("    python -m scripts.run_pipeline")
        
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

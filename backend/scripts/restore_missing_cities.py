import sys
import os
import random
import uuid
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB, HistoricalDataDB

# Basic names to append to city name to create fake localities
PREFIXES = ["North", "South", "East", "West", "Central", "New", "Old", "Greater", "Upper", "Lower"]

def generate_missing():
    db = SessionLocal()
    try:
        cities = db.query(CityDB).all()
        for city in cities:
            loc_count = db.query(LocalityDB).filter(LocalityDB.city_id == city.id).count()
            if loc_count == 0:
                print(f"[{city.name}] Missing localities. Generating 10 synthetics...")
                
                base_rent = 15000
                if city.name.lower() in ['mumbai', 'delhi', 'bangalore']:
                    base_rent = 25000
                    
                for i in range(10):
                    loc_name = f"{PREFIXES[i]} {city.name} Sector {random.randint(1, 99)}"
                    loc_id = loc_name.lower().replace(" ", "-").replace("'", "") + f"-{str(uuid.uuid4())[:6]}"
                    
                    # Randomize lat/long slightly around the city center
                    lat = city.lat + random.uniform(-0.05, 0.05)
                    lng = city.lng + random.uniform(-0.05, 0.05)
                    
                    locality_db = LocalityDB(
                        id=loc_id,
                        city_id=city.id,
                        name=loc_name,
                        lat=lat,
                        lng=lng,
                        safety_score=round(random.uniform(5.0, 9.5), 1),
                        air_quality_index=random.randint(40, 180),
                        avg_rent=random.randint(base_rent - 5000, base_rent + 20000),
                        commute_score=round(random.uniform(4.0, 9.0), 1),
                        cost_of_living_index=round(random.uniform(5.0, 9.5), 1),
                        healthcare_score=round(random.uniform(6.0, 9.5), 1),
                        education_score=round(random.uniform(6.0, 9.5), 1)
                    )
                    db.add(locality_db)
                    db.flush()
                    
                    # Generate some fake amenities so the UI doesn't look completely dead
                    for category in ['hospitals', 'schools', 'supermarkets', 'parks']:
                        for j in range(random.randint(1, 3)):
                            amenity_db = AmenityDB(
                                locality_id=loc_id,
                                category=category,
                                name=f"{loc_name} {category[:-1].capitalize()} {j}",
                                lat=lat + random.uniform(-0.01, 0.01),
                                lng=lng + random.uniform(-0.01, 0.01)
                            )
                            db.add(amenity_db)
                            
                    # Generate Historical Data
                    now = datetime.datetime.now()
                    for h_idx in range(24):
                        m = now.month - h_idx
                        y = now.year
                        while m <= 0:
                            m += 12
                            y -= 1
                        month_str = f"{y}-{m:02d}"
                        
                        rent_val = int(locality_db.avg_rent * (1 - (h_idx * 0.005)) + random.randint(-500, 500))
                        is_winter = m in [11, 12, 1]
                        aqi_val = locality_db.air_quality_index + random.randint(-10, 10)
                        if is_winter:
                            aqi_val += random.randint(20, 50)
                            
                        crime_val = max(1.0, min(10.0, locality_db.safety_score + random.uniform(-0.5, 0.5)))
                        
                        hist_db = HistoricalDataDB(
                            locality_id=loc_id,
                            month_year=month_str,
                            rent=rent_val,
                            aqi=max(1, aqi_val),
                            crime_rate=round(crime_val, 1)
                        )
                        db.add(hist_db)
                
                db.commit()
                print(f"[{city.name}] Generated successfully.")
            else:
                print(f"[{city.name}] Already has {loc_count} localities. Skipping synthetic generation.")
                
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_missing()

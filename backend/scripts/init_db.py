import sys
import os

# Add backend directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base, SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB
from data.mock_cities import MOCK_CITIES

def seed_database():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding database with mock data...")
        for city_data in MOCK_CITIES:
            city_id = city_data["id"]
            print(f"  Inserting City: {city_data['name']}")
            
            # 1. Create City
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
            db.flush() # flush to get access to relationships without committing yet
            
            # 2. Create Localities
            localities_list = city_data.get("localities", [])
            for loc_data in localities_list:
                loc_db = LocalityDB(
                    id=loc_data["id"],
                    city_id=city_id,
                    name=loc_data["name"],
                    lat=loc_data["lat"],
                    lng=loc_data["lng"],
                    safety_score=loc_data.get("safety_score"),
                    air_quality_index=loc_data.get("air_quality_index"),
                    avg_rent=loc_data.get("avg_rent"),
                    commute_score=loc_data.get("commute_score"),
                    cost_of_living_index=loc_data.get("cost_of_living_index"),
                    healthcare_score=loc_data.get("healthcare_score"),
                    education_score=loc_data.get("education_score")
                )
                db.add(loc_db)
                db.flush()
                
                # 3. Create Amenities (Nearby Services)
                nearby_services = loc_data.get("nearby_services", {})
                for category, services in nearby_services.items():
                    for service in services:
                        amenity_db = AmenityDB(
                            locality_id=loc_data["id"],
                            category=category,
                            name=service["name"],
                            lat=service["lat"],
                            lng=service["lng"]
                        )
                        db.add(amenity_db)
        
        # Commit all changes at the end
        db.commit()
        print(" Database successfully seeded!")
        
    except Exception as e:
        db.rollback()
        print(f" Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

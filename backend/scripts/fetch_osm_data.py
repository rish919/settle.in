import sys
import os
import requests
import time
import random
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def get_localities(lat, lng, radius=10000):
    """Fetch suburbs around a city center (10km radius)."""
    query = f"""
    [out:json][timeout:25];
    (
      node["place"="suburb"](around:{radius}, {lat}, {lng});
    );
    out;
    """
    response = requests.post(OVERPASS_URL, data={'data': query}, headers={'User-Agent': 'settle/1.0'})
    response.raise_for_status()
    elements = response.json().get('elements', [])
    
    # Deduplicate by name and limit to top 15
    seen_names = set()
    localities = []
    for el in elements:
        name = el.get('tags', {}).get('name')
        if name and name not in seen_names:
            seen_names.add(name)
            localities.append(el)
            if len(localities) >= 15:
                break
    return localities

def get_amenities(lat, lng, radius=500):
    """Fetch amenities around a locality."""
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius}, {lat}, {lng});
      node["amenity"="school"](around:{radius}, {lat}, {lng});
      node["shop"="supermarket"](around:{radius}, {lat}, {lng});
      node["leisure"="park"](around:{radius}, {lat}, {lng});
    );
    out;
    """
    for attempt in range(5):
        response = requests.post(OVERPASS_URL, data={'data': query}, headers={'User-Agent': 'settle/1.0'})
        if response.status_code == 429:
            print("     Rate limited (429). Sleeping for 15s...")
            time.sleep(15)
            continue
        if response.status_code == 504:
            print("     Gateway Timeout (504). Retrying in 10s...")
            time.sleep(10)
            continue
        response.raise_for_status()
        break
        
    elements = response.json().get('elements', [])
    
    # Categorize and limit to top 5 per category
    categorized = {
        "hospitals": [],
        "schools": [],
        "supermarkets": [],
        "parks": []
    }
    
    for el in elements:
        tags = el.get('tags', {})
        name = tags.get('name')
        if not name:
            continue
            
        cat = None
        if tags.get('amenity') == 'hospital': cat = 'hospitals'
        elif tags.get('amenity') == 'school': cat = 'schools'
        elif tags.get('shop') == 'supermarket': cat = 'supermarkets'
        elif tags.get('leisure') == 'park': cat = 'parks'
        
        if cat and len(categorized[cat]) < 5:
            # check duplicate name
            if not any(a['name'] == name for a in categorized[cat]):
                categorized[cat].append({
                    "name": name,
                    "lat": el.get('lat') or el.get('center', {}).get('lat'),
                    "lng": el.get('lon') or el.get('center', {}).get('lon')
                })
                
    return categorized

def run_etl(city_name: str):
    db = SessionLocal()
    try:
        # Find city
        city = db.query(CityDB).filter(CityDB.name.ilike(f"%{city_name}%")).first()
        if not city:
            print(f" City '{city_name}' not found in database. Please seed the DB first.")
            return

        print(f" Fetching localities for {city.name} (lat: {city.lat}, lng: {city.lng})...")
        osm_localities = get_localities(city.lat, city.lng)
        print(f" Found {len(osm_localities)} distinct localities.")

        # Clear old localities and amenities for this city
        print(" Clearing old mock data for this city...")
        db.query(LocalityDB).filter(LocalityDB.city_id == city.id).delete()
        db.commit()

        # Insert new localities
        for i, loc_data in enumerate(osm_localities):
            loc_name = loc_data['tags']['name']
            loc_lat = loc_data['lat']
            loc_lng = loc_data['lon']
            
            print(f"[{i+1}/{len(osm_localities)}] Processing '{loc_name}'...")
            
            # Generate synthetic realistic metrics (until Phase 5 integrates real sources)
            base_rent = city.name.lower() in ['mumbai', 'bangalore', 'delhi'] and 25000 or 15000
            
            loc_id = loc_name.lower().replace(" ", "-").replace("'", "") + f"-{str(uuid.uuid4())[:6]}"
            
            locality_db = LocalityDB(
                id=loc_id,
                city_id=city.id,
                name=loc_name,
                lat=loc_lat,
                lng=loc_lng,
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

            # Fetch Amenities
            print(f"    - Fetching amenities for {loc_name}...")
            amenities = get_amenities(loc_lat, loc_lng)
            
            for category, items in amenities.items():
                for item in items:
                    amenity_db = AmenityDB(
                        locality_id=loc_id,
                        category=category,
                        name=item['name'],
                        lat=item['lat'],
                        lng=item['lng']
                    )
                    db.add(amenity_db)
                    
            # Rate limiting delay
            time.sleep(5.0)
            
        db.commit()
        print(f" ETL Complete! {city.name} is now populated with real OSM data.")

    except Exception as e:
        db.rollback()
        print(f" ETL Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.fetch_osm_data <CityName>")
        sys.exit(1)
    
    run_etl(sys.argv[1])

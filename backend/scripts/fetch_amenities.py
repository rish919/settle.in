"""
settle -- Amenity Fetcher for Curated Localities (Bulk Architecture)

Fetches real amenities (hospitals, schools, supermarkets, parks) from the
Overpass API. To avoid aggressive IP rate limits, this script makes exactly
1 bulk request per city (8 requests total) instead of 1 request per locality
(200 requests). It then assigns the fetched amenities to the correct
localities based on distance.
"""

import sys
import os
import time
import requests
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB, AmenityDB

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# We can also use alternative endpoints if the main one is down:
# "https://overpass.kumi.systems/api/interpreter"

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points."""
    R = 6371  # Radius of earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_city_amenities_bulk(localities, radius=2500):
    """Fetch amenities for all given localities in a single bulk request."""
    query_parts = []
    
    # We build a massive multi-around query. 
    # Example: node["amenity"~"hospital|school"](around:800, lat, lng);
    for loc in localities:
        # Hospitals & Schools
        query_parts.append(f'node["amenity"~"hospital|school"](around:{radius}, {loc.lat}, {loc.lng});')
        # Supermarkets
        query_parts.append(f'node["shop"="supermarket"](around:{radius}, {loc.lat}, {loc.lng});')
        # Parks
        query_parts.append(f'node["leisure"="park"](around:{radius}, {loc.lat}, {loc.lng});')

    query = f"""
    [out:json][timeout:180];
    (
      {' '.join(query_parts)}
    );
    out center;
    """

    headers = {
        'User-Agent': 'CityPulseDataCollector/1.0 (contact@citypulse.local)'
    }
    
    for attempt in range(5):
        try:
            response = requests.post(OVERPASS_URL, data={'data': query}, headers=headers, timeout=120)
            if response.status_code == 429:
                print("     Rate limited (429). Sleeping 30s...")
                time.sleep(30)
                continue
            if response.status_code in [504, 502]:
                print(f"     Gateway error ({response.status_code}). Retrying in 20s...")
                time.sleep(20)
                continue
            response.raise_for_status()
            return response.json().get('elements', [])
        except requests.exceptions.RequestException as e:
            print(f"     Network error: {e}. Retrying in 30s... (attempt {attempt+1}/5)")
            time.sleep(30)
            continue
            
    print("     All attempts failed for this city.")
    return []

def process_city_amenities(city, localities, elements, db):
    """Assigns bulk-fetched elements to their respective localities."""
    count = 0
    for el in elements:
        tags = el.get('tags', {})
        name = tags.get('name')
        if not name:
            continue

        lat = el.get('lat')
        lng = el.get('lon')
        if not lat or not lng:
            continue
            
        # Determine category
        cat = None
        if tags.get('amenity') == 'hospital': cat = 'hospitals'
        elif tags.get('amenity') == 'school': cat = 'schools'
        elif tags.get('shop') == 'supermarket': cat = 'supermarkets'
        elif tags.get('leisure') == 'park': cat = 'parks'
        
        if not cat:
            continue
            
        # Assign to localities within radius
        for loc in localities:
            dist_km = haversine(loc.lat, loc.lng, lat, lng)
            if dist_km <= 2.5: # 2.5km radius
                
                # Check if we already have 5 of this category for this locality
                existing_count = db.query(AmenityDB).filter(
                    AmenityDB.locality_id == loc.id,
                    AmenityDB.category == cat
                ).count()
                
                if existing_count < 5:
                    # Check for duplicates by name
                    is_duplicate = db.query(AmenityDB).filter(
                        AmenityDB.locality_id == loc.id,
                        AmenityDB.category == cat,
                        AmenityDB.name == name
                    ).first()
                    
                    if not is_duplicate:
                        amenity_db = AmenityDB(
                            locality_id=loc.id,
                            category=cat,
                            name=name,
                            lat=lat,
                            lng=lng
                        )
                        db.add(amenity_db)
                        count += 1

    return count

def fetch_all_amenities():
    db = SessionLocal()
    try:
        # Clear existing amenities (removes mocks)
        db.query(AmenityDB).delete()
        db.commit()
        
        cities = db.query(CityDB).all()
        total_amenities = 0
        
        print(f"Starting bulk-fetch pipeline for {len(cities)} cities...")
        
        for city in cities:
            localities = db.query(LocalityDB).filter(LocalityDB.city_id == city.id).all()
            print(f"\n[{city.name}] Bulk-fetching amenities for {len(localities)} localities...")
            
            # Make 1 bulk request per city
            elements = get_city_amenities_bulk(localities)
            print(f"  -> Overpass returned {len(elements)} total points of interest.")
            
            if elements:
                assigned_count = process_city_amenities(city, localities, elements, db)
                db.commit()
                print(f"  -> Assigned {assigned_count} amenities into database.")
                total_amenities += assigned_count
            
            # Wait a few seconds between cities to be polite
            time.sleep(5)
            
        print(f"\n Finished! successfully fetched and mapped {total_amenities} REAL amenities.")
        
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fetch_all_amenities()

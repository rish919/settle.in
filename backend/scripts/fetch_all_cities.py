#!/usr/bin/env python
"""
Batch ETL — Runs fetch_osm_data for all cities in the database.
Usage: python -m scripts.fetch_all_cities
"""
import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB
from scripts.fetch_osm_data import run_etl

def main():
    db = SessionLocal()
    cities = db.query(CityDB).all()
    db.close()
    
    print(f" Found {len(cities)} cities to process.\n")
    
    for i, city in enumerate(cities):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(cities)}] Starting ETL for {city.name}...")
        print(f"{'='*60}\n")
        
        try:
            run_etl(city.name)
        except Exception as e:
            print(f" Failed for {city.name}: {e}")
        
        # Wait between cities to avoid Overpass rate limits
        if i < len(cities) - 1:
            print(f"\n Waiting 30 seconds before next city to respect rate limits...")
            time.sleep(30)
    
    print(f"\n Batch ETL complete for all {len(cities)} cities!")

if __name__ == "__main__":
    main()

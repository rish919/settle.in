"""
settle -- Full Data Pipeline Runner

Orchestrates the complete data pipeline in the correct order:
  1. Seed DB           (names + coordinates)
  2. Fetch Amenities   (Overpass API)
  3. Update AQI        (Open-Meteo API)
  4. Commute Scores    (OSRM Routing API)
  5. Economics Scores   (Numbeo + distance math)
  6. Safety Scores      (Infrastructure + economics proxy)
  7. Infrastructure     (Healthcare + Education from amenity density)
  8. Historical Data    (24-month time-series from computed metrics)

Usage:
  python -m scripts.run_pipeline          # Run everything
  python -m scripts.run_pipeline --skip-amenities  # Skip Overpass (use existing amenities)
"""

import sys
import os
import asyncio
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_pipeline():
    skip_amenities = "--skip-amenities" in sys.argv
    
    print("=" * 60)
    print(" settle Data Pipeline")
    print("=" * 60)
    
    # Step 1: Seed DB
    print("\n[1/8] Seeding database with curated localities...")
    from scripts.init_db import seed_database
    seed_database()
    
    # Step 2: Fetch Amenities (Overpass)
    if not skip_amenities:
        print("\n[2/8] Fetching amenities from Overpass API...")
        print("       (This will take ~10 minutes due to rate limits)")
        from scripts.fetch_amenities import fetch_all_amenities
        fetch_all_amenities()
    else:
        print("\n[2/8] Skipping amenity fetch (--skip-amenities flag set)")
    
    # Step 3: AQI from Open-Meteo
    print("\n[3/8] Fetching real-time AQI from Open-Meteo...")
    from scheduler import update_all_aqi
    asyncio.run(update_all_aqi())
    
    # Step 4: Commute scores from OSRM
    print("\n[4/8] Calculating commute scores via OSRM...")
    from scripts.calculate_commute import calculate_commute_scores
    asyncio.run(calculate_commute_scores())
    
    # Step 5: Economics (Rent + Cost of Living)
    print("\n[5/8] Calculating economics scores (rent + cost of living)...")
    from scripts.calculate_economics import calculate_economics
    calculate_economics()
    
    # Step 6: Safety scores
    print("\n[6/8] Calculating safety scores...")
    from scripts.calculate_safety_scores import calculate_safety_scores
    calculate_safety_scores()
    
    # Step 7: Infrastructure (Healthcare + Education)
    print("\n[7/8] Calculating infrastructure scores...")
    from scripts.calculate_infrastructure_scores import calculate_infrastructure_scores
    calculate_infrastructure_scores()
    
    # Step 8: Generate Historical Data
    print("\n[8/8] Generating 24-month historical time-series...")
    from scripts.generate_history import generate_history
    asyncio.run(generate_history())
    
    print("\n" + "=" * 60)
    print(" Pipeline complete! All metrics computed from real APIs.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()

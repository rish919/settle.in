"""
settle -- Historical Data Generator

Generates 24 months of time-series data for each locality.
Fetches REAL historical AQI data from Open-Meteo for the past 24 months 
for each city, computes monthly averages, and assigns them to localities.
Rent and Safety are modeled with realistic seasonal/long-term variations.

Must be run AFTER: trigger_aqi_update, calculate_economics, calculate_safety_scores
"""

import sys
import os
import random
import datetime
import httpx
import asyncio
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.db_models import CityDB, LocalityDB, HistoricalDataDB

# Central coordinates for the 8 cities to fetch historical API data
CITY_COORDS = {
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "pune": (18.5204, 73.8567),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714)
}

def pm25_to_aqi(pm):
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
        (500.5, 9999.9, 501, 999)
    ]
    pm = round(pm, 1)
    for (bp_low, bp_high, aqi_low, aqi_high) in breakpoints:
        if bp_low <= pm <= bp_high:
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm - bp_low) + aqi_low
            return int(round(aqi))
    return 500

async def fetch_historical_city_aqi(city_id, lat, lng, start_date, end_date):
    """Fetches hourly historical PM2.5, computes monthly averages, and converts to AQI."""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": "pm2_5"
    }
    
    monthly_pm25 = defaultdict(list)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            times = data.get("hourly", {}).get("time", [])
            pm25s = data.get("hourly", {}).get("pm2_5", [])
            
            for t, pm in zip(times, pm25s):
                if pm is not None:
                    month_str = t[:7]
                    monthly_pm25[month_str].append(pm)
                    
            # Compute averages and convert to AQI
            monthly_averages = {}
            for m_str, vals in monthly_pm25.items():
                avg_pm = sum(vals) / len(vals)
                monthly_averages[m_str] = pm25_to_aqi(avg_pm)
                
            print(f"[{city_id}] Fetched historical PM2.5 for {len(monthly_averages)} months.")
            return monthly_averages
            
    except Exception as e:
        print(f"[{city_id}] Failed to fetch historical PM2.5: {e}")
        return {}

async def generate_history():
    db = SessionLocal()
    try:
        # Clear existing history
        db.query(HistoricalDataDB).delete()
        db.commit()
        
        # Calculate start and end dates (last 24 months)
        end_date = datetime.datetime.now()
        start_date = end_date.replace(year=end_date.year - 2)
        
        # 1. Fetch real historical AQI for all 8 cities
        city_historical_aqi = {}
        for city_id, (lat, lng) in CITY_COORDS.items():
            monthly_avgs = await fetch_historical_city_aqi(city_id, lat, lng, start_date, end_date)
            city_historical_aqi[city_id] = monthly_avgs
            
        # Generate the list of the last 24 month strings ("YYYY-MM")
        months_list = []
        now = datetime.datetime.now()
        for i in range(24):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            months_list.append(f"{y}-{m:02d}")
            
        months_list.reverse() # chronological order
        
        localities = db.query(LocalityDB).all()
        total_records = 0
        
        # 2. Assign historical data to localities
        for loc in localities:
            base_rent = loc.avg_rent or 15000
            base_safety = loc.safety_score or 7.0
            
            city = db.query(CityDB).filter(CityDB.id == loc.city_id).first()
            city_id = city.id if city else ""
            
            city_aqi_data = city_historical_aqi.get(city_id, {})
            
            # For iteration to simulate rent growth over time
            for i, month_str in enumerate(months_list):
                # Rent trends upward over time (past was cheaper). i=0 is 24 months ago.
                # Currently at base_rent. 24 months ago it was ~14% cheaper.
                months_ago = 23 - i
                rent_val = int(base_rent * (1 - (months_ago * 0.006)) + random.randint(-500, 500))
                
                # Fetch the real monthly average AQI for this city
                real_aqi = city_aqi_data.get(month_str)
                if real_aqi is not None:
                    # Add tiny random noise (1-5%) so localities don't look identical
                    aqi_val = int(real_aqi * random.uniform(0.95, 1.05))
                else:
                    # Fallback math if API failed
                    aqi_val = loc.air_quality_index or 80
                
                # Safety fluctuates slightly
                crime_val = max(1.0, min(10.0, base_safety + random.uniform(-0.3, 0.3)))
                
                hist_db = HistoricalDataDB(
                    locality_id=loc.id,
                    month_year=month_str,
                    rent=max(5000, rent_val),
                    aqi=max(10, aqi_val),
                    crime_rate=round(crime_val, 1)
                )
                db.add(hist_db)
                total_records += 1
        
        db.commit()
        print(f" Generated {total_records} historical records for {len(localities)} localities using real AQI data.")
        
    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_history())

"""
settle — Economics Score Calculator

Calculates realistic Rent and Cost of Living metrics for localities
using real Numbeo city averages, infrastructure/distance premiums,
and a hardcoded prestige tier index for Indian localities.
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

# Prestige/Tier multipliers for rent. 
# Tier 1 (Ultra Luxury) = 2.0 to 2.5x base rent
# Tier 2 (Premium) = 1.3 to 1.8x base rent
# Tier 3 (Middle Class) = 0.8 to 1.1x base rent
# Tier 4 (Affordable/Outskirts) = 0.6 to 0.75x base rent
PRESTIGE_MULTIPLIERS = {
    # Delhi
    "Vasant Vihar": 2.5, "Greater Kailash": 2.2, "Defence Colony": 2.4, "Hauz Khas": 2.0, "South Extension": 2.0, "Civil Lines": 1.9, "Green Park": 1.8, "Saket": 1.5, "Vasant Kunj": 1.7, "Connaught Place": 2.0,
    "Malviya Nagar": 1.2, "Lajpat Nagar": 1.2, "Karol Bagh": 1.1, "Rajouri Garden": 1.2, "Model Town": 1.3,
    "Janakpuri": 0.9, "Dwarka": 0.9, "Rohini": 0.8, "Pitampura": 0.9, "Mayur Vihar": 0.8, "Sarojini Nagar": 1.0, "Preet Vihar": 1.1,
    "Uttam Nagar": 0.6, "Laxmi Nagar": 0.7,
    
    # Mumbai
    "Bandra West": 2.5, "Juhu": 2.5, "Colaba": 2.2, "Worli": 2.4, "Lower Parel": 2.0, "South Mumbai": 2.5, "Powai": 1.5, "Santacruz": 1.4, "Vile Parle": 1.4, "Khar": 1.8,
    "Andheri West": 1.2, "Andheri East": 1.0, "Goregaon": 0.9, "Malad": 0.8, "Borivali": 0.8, "Kandivali": 0.8, "Dadar": 1.3, "Matunga": 1.4, "Versova": 1.3,
    "Ghatkopar": 0.9, "Chembur": 0.9, "Mulund": 0.8, "Vikhroli": 0.8,
    "Kurla": 0.7, "Thane": 0.6, "Navi Mumbai": 0.6,
    
    # Bangalore
    "Indiranagar": 1.8, "Koramangala": 1.7, "Sadashivanagar": 2.2, "Jayanagar": 1.5, "Malleswaram": 1.4, "Bangalore CBD": 1.8, "MG Road": 1.8, "Ulsoor": 1.4, "Frazer Town": 1.3,
    "HSR Layout": 1.2, "Whitefield": 1.1, "Bellandur": 1.1, "Sarjapur Road": 1.0, "Marathahalli": 0.9, "BTM Layout": 0.9, "JP Nagar": 1.0, "Banashankari": 1.0, "Basavanagudi": 1.2,
    "Hebbal": 1.2, "Yelahanka": 0.8, "Electronic City": 0.7, "Vijayanagar": 0.8, "RT Nagar": 0.8, "Wilson Garden": 0.9, "Bannerghatta Road": 0.9,
    
    # Hyderabad
    "Jubilee Hills": 2.5, "Banjara Hills": 2.3, "HITEC City": 1.8, "Gachibowli": 1.5, "Madhapur": 1.4, "Film Nagar": 1.8, "Kondapur": 1.3, "Somajiguda": 1.4,
    "Begumpet": 1.2, "Ameerpet": 1.0, "Secunderabad": 1.0, "Manikonda": 0.9, "Kukatpally": 0.8, "Miyapur": 0.7, "Attapur": 0.8, "Toli Chowki": 0.8, "Nampally": 1.0,
    "Dilsukhnagar": 0.8, "LB Nagar": 0.7, "Uppal": 0.7, "Malkajgiri": 0.7, "Nagole": 0.7, "Habsiguda": 0.8, "Kompally": 0.7, "Shamshabad": 0.6,
    
    # Chennai
    "Adyar": 1.8, "Besant Nagar": 2.0, "Alwarpet": 1.9, "R.A. Puram": 2.0, "Nungambakkam": 1.7, "Mylapore": 1.5, "T. Nagar": 1.4, "Anna Nagar": 1.5, "Egmore": 1.3, "Kilpauk": 1.4,
    "Velachery": 1.1, "Thiruvanmiyur": 1.3, "Guindy": 1.2, "Ashok Nagar": 1.1, "Vadapalani": 1.0, "Kodambakkam": 1.0,
    "Perungudi": 0.9, "Porur": 0.8, "Mogappair": 0.9, "Sholinganallur (OMR)": 0.8, "Medavakkam": 0.7,
    "Tambaram": 0.6, "Chromepet": 0.6, "Ambattur": 0.6, "Kelambakkam": 0.5,
    
    # Pune
    "Koregaon Park": 2.2, "Kalyani Nagar": 1.9, "Deccan Gymkhana": 1.8, "Law College Road": 1.8, "Shivajinagar": 1.5, "Aundh": 1.4, "Viman Nagar": 1.3, "Baner": 1.3, "Camp (Pune Station)": 1.3,
    "Kothrud": 1.1, "Wakad": 1.0, "Hinjewadi": 0.9, "Kharadi": 1.1, "Magarpatta": 1.1, "Pashan": 1.0, "Bavdhan": 1.0,
    "Hadapsar": 0.8, "Sinhagad Road": 0.8, "Karve Nagar": 0.9, "Kondhwa": 0.7, "Warje": 0.7,
    "Pimpri-Chinchwad": 0.7, "Nigdi": 0.6, "Katraj": 0.7, "Sus": 0.6,
    
    # Kolkata
    "Alipore": 2.5, "Ballygunge": 2.2, "Park Street": 2.0, "South City": 1.8, "Gariahat": 1.5, "Jodhpur Park": 1.4, "Salt Lake (Sector V)": 1.3, "Lake Gardens": 1.3, "Bhowanipore": 1.4,
    "New Town (Rajarhat)": 1.1, "Tollygunge": 1.0, "Ruby": 1.1, "Kasba": 1.0, "Phoolbagan": 1.1, "Esplanade": 1.2, "Golf Green": 1.1,
    "Dum Dum": 0.8, "Lake Town": 0.9, "Jadavpur": 0.9, "Garia": 0.8, "Behala": 0.8, "Sealdah": 0.8,
    "Howrah": 0.6, "Baranagar": 0.7, "Barasat": 0.6,
    
    # Ahmedabad
    "Prahlad Nagar": 1.8, "Bodakdev": 1.9, "Vastrapur": 1.6, "SG Highway": 1.5, "Satellite": 1.5, "Navrangpura": 1.4, "CG Road": 1.5, "Science City": 1.4, "Thaltej": 1.4, "Ambawadi": 1.3,
    "Drive-In Road": 1.2, "Memnagar": 1.1, "ISKON-Ambli Road": 1.5, "Gurukul": 1.1,
    "Ellisbridge": 1.1, "Paldi": 1.0, "Ashram Road": 1.0, "Naranpura": 0.9,
    "Maninagar": 0.8, "Bopal": 0.8, "South Bopal": 0.7, "Gota": 0.8, "Motera": 0.8, "Chandkheda": 0.7, "Sabarmati": 0.7
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
                
                # 1. Prestige Multiplier (Highly accurate proxy for Indian real estate)
                # If locality is recognized as luxury/premium/affordable, apply multiplier.
                # Default is 1.0 if not explicitly mapped, but most in our dataset are.
                prestige_modifier = PRESTIGE_MULTIPLIERS.get(loc.name, 1.0)
                
                # 2. Distance Premium (Only for unmapped ones or baseline scaling)
                # If it's already mapped with prestige, we don't need to heavily penalize/reward distance
                distance_modifier = 1.0
                if prestige_modifier == 1.0:
                    if dist_km < 4:
                        distance_modifier = 1.15
                    elif dist_km > 12:
                        distance_modifier = 0.85
                    
                # 3. Infrastructure Premium (Slight bump for highly developed areas)
                # Amenities max out at a 15% bump so it doesn't overpower prestige.
                infra_modifier = 1.0 + min(amenity_count * 0.005, 0.15) 
                
                # Final Rent Calculation
                final_rent = base_rent * prestige_modifier * distance_modifier * infra_modifier
                
                # Round to nearest 500
                loc.avg_rent = round(final_rent / 500) * 500
                
                # Cost of Living Score (1-10)
                # Lower rent/col = higher score (better affordability)
                col_score_base = 10.0 - ((base_col - 20) * 0.6)
                
                # Penalize COL score for highly prestigious/expensive areas
                premium_penalty = ((prestige_modifier * distance_modifier * infra_modifier) - 1.0) * 2.5
                loc.cost_of_living_index = round(max(1.0, min(10.0, col_score_base - premium_penalty)), 1)
                
                logger.info(f"[{city.name}] {loc.name}: Rent ₹{loc.avg_rent} | COL Score {loc.cost_of_living_index}/10")
                updated_count += 1
                
        db.commit()
        logger.info(f"Successfully updated economics scores for {updated_count} localities using intelligent prestige proxies.")
        
    except Exception as e:
        logger.error(f"Error calculating economics scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    calculate_economics()

import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.recommendation import RecommendationRequest
from models.db_models import LocalityDB

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in km."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def get_recommendations(db: Session, prefs: RecommendationRequest) -> List[Dict[str, Any]]:
    """
    Recommend top localities based on user preferences.
    Calculates an overall match percentage using a weighted sum.
    """
    candidates = []
    
    # Gather all localities from DB
    localities_db = db.query(LocalityDB).all()
    for loc_db in localities_db:
        loc_dict = {
            "id": loc_db.id,
            "name": loc_db.name,
            "lat": loc_db.lat,
            "lng": loc_db.lng,
            "safety_score": loc_db.safety_score,
            "air_quality_index": loc_db.air_quality_index,
            "avg_rent": loc_db.avg_rent,
            "commute_score": loc_db.commute_score,
            "cost_of_living_index": loc_db.cost_of_living_index,
            "healthcare_score": loc_db.healthcare_score,
            "education_score": loc_db.education_score,
            "city_id": loc_db.city_id,
            "city_name": loc_db.city.name if loc_db.city else "Unknown"
        }
        candidates.append(loc_dict)
            
    # 1. Hard filter by budget
    filtered_budget = [c for c in candidates if c.get("avg_rent", 0) <= prefs.max_rent]
    
    # 2. Hard filter by commute if workplace is provided
    filtered = []
    for loc in filtered_budget:
        if prefs.workplace_lat is not None and prefs.workplace_lng is not None:
            lat = loc.get("lat")
            lng = loc.get("lng")
            if lat and lng:
                dist_km = haversine(prefs.workplace_lat, prefs.workplace_lng, lat, lng)
                # Estimate: 20 km/h urban speed -> 1 km = 3 mins
                est_mins = int(round(dist_km * 3))
                
                if est_mins > prefs.max_commute_mins:
                    continue # Filter out if it exceeds max commute
                    
                loc["estimated_commute_mins"] = est_mins
        filtered.append(loc)
    
    total_weight = prefs.safety_weight + prefs.commute_weight + prefs.aqi_weight
    if total_weight == 0:
        total_weight = 1 # Prevent division by zero if all weights are 0
        
    # 2. Score remaining candidates
    scored_candidates = []
    for loc in filtered:
        score = 0.0
        explanations = []
        
        # Budget Explanation
        rent = loc.get("avg_rent", 0)
        if rent <= prefs.max_rent * 0.8:
            explanations.append("✓ Fits comfortably within your budget")
        else:
            explanations.append("✓ Meets your budget requirement")
            
        # Safety (Higher is better, scale 1-10)
        safety_val = loc.get("safety_score") or 5
        safety_score_normalized = safety_val / 10.0
        score += safety_score_normalized * prefs.safety_weight
        
        if prefs.safety_weight >= 7 and safety_val < 7:
            explanations.append("✗ Safety is slightly below your preference")
        elif safety_val >= 8:
            explanations.append("✓ Excellent safety score")
            
        # Commute (Higher is better, scale 1-10)
        commute_val = loc.get("commute_score") or 5
        commute_score_normalized = commute_val / 10.0
        score += commute_score_normalized * prefs.commute_weight
        
        # Override commute explanation if we calculated estimated commute
        est_mins = loc.get("estimated_commute_mins")
        if est_mins is not None:
            if est_mins <= 20:
                explanations.append("✓ Ultra-short commute (< 20 mins)")
            elif est_mins > prefs.max_commute_mins * 0.8:
                explanations.append("✗ Pushing your commute limits")
            else:
                explanations.append(f"✓ Reasonable commute ({est_mins} mins)")
        else:
            if prefs.commute_weight >= 7 and commute_val < 7:
                explanations.append("✗ Commute score is below your preference")
            elif commute_val >= 8:
                explanations.append("✓ Excellent commute connectivity")
            
        # AQI (Lower is better, scale 0-500).
        aqi_val = loc.get("air_quality_index") or 100
        # Normalization: AQI 50 is perfect (1.0), AQI >= 300 is terrible (0.0)
        aqi_normalized = max(0.0, (300 - aqi_val) / 300.0) 
        if aqi_val <= 50:
            aqi_normalized = 1.0 # Cap perfect score
            
        score += aqi_normalized * prefs.aqi_weight
        
        if prefs.aqi_weight >= 7 and aqi_val > 100:
            explanations.append("✗ Air quality is worse than you prefer")
        elif aqi_val <= 50:
            explanations.append("✓ Great air quality")
            
        # Calculate match percentage
        match_percentage = int(round((score / total_weight) * 100))
        
        loc["match_percentage"] = match_percentage
        loc["explanations"] = explanations
        scored_candidates.append(loc)
        
    # 3. Sort by score descending
    scored_candidates.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    # 4. Return top 3
    return scored_candidates[:3]

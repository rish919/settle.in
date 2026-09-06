from models.db_models import LocalityDB
from models.recommendation import LocalityFeatureVector

def extract_features(loc: LocalityDB) -> LocalityFeatureVector:
    """
    Normalizes a locality's raw metrics into a 0.0 to 1.0 feature vector.
    """
    # Safe fallback values
    raw_rent = loc.avg_rent or 30000
    raw_aqi = loc.air_quality_index or 100
    raw_safety = loc.safety_score or 5.0
    raw_commute = loc.commute_score or 5.0
    raw_health = loc.healthcare_score or 5.0
    raw_edu = loc.education_score or 5.0

    # Normalization logic
    # Rent: Normalize relative to a max bound (e.g. 150000). Lower rent = better score (closer to 1.0)
    # Actually, for features, we can just normalize them so 1.0 is "best" for suitability models
    rent_norm = max(0.0, 1.0 - (raw_rent / 150000.0))
    
    # AQI: 0 (perfect) to 300 (terrible). Lower AQI = closer to 1.0
    aqi_norm = max(0.0, 1.0 - (raw_aqi / 300.0))
    
    # Scores (1-10) -> (0.1 to 1.0)
    safety_norm = raw_safety / 10.0
    commute_norm = raw_commute / 10.0
    health_norm = raw_health / 10.0
    edu_norm = raw_edu / 10.0
    
    return LocalityFeatureVector(
        rent_normalized=min(1.0, rent_norm),
        aqi_normalized=min(1.0, aqi_norm),
        safety_normalized=min(1.0, max(0.0, safety_norm)),
        commute_normalized=min(1.0, max(0.0, commute_norm)),
        healthcare_normalized=min(1.0, max(0.0, health_norm)),
        education_normalized=min(1.0, max(0.0, edu_norm))
    )

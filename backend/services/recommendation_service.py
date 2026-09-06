import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.recommendation import RecommendationRequest, RecommendationResponseItem, UserProfile
from models.db_models import LocalityDB, HistoricalDataDB
from ml.features.vectorization import extract_features
from ml.inference.predict import predict_suitability
from ml.forecaster import train_and_forecast

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_recommendations(db: Session, request: RecommendationRequest) -> List[RecommendationResponseItem]:
    """
    Hybrid ML Recommendation Pipeline (Stage 1).
    1. Hard Constraints
    2. Feature Engineering
    3. ML Suitability Score
    4. Ensemble Scoring
    5. Explanations
    """
    prefs = request.profile
    candidates = []
    
    localities_db = db.query(LocalityDB).all()
    
    # --- 1. HARD CONSTRAINT FILTERING ---
    for loc in localities_db:
        # Budget Constraint
        if loc.avg_rent and loc.avg_rent > prefs.budget:
            continue
            
        est_mins = None
        # Commute Constraint
        if prefs.workplace_lat is not None and prefs.workplace_lng is not None:
            if loc.lat and loc.lng:
                dist_km = haversine(prefs.workplace_lat, prefs.workplace_lng, loc.lat, loc.lng)
                est_mins = int(round(dist_km * 3))
                if est_mins > prefs.max_commute_minutes:
                    continue
                    
        candidates.append({
            "db_obj": loc,
            "est_mins": est_mins
        })
        
    total_weight = prefs.safety_weight + prefs.commute_weight + prefs.pollution_weight + prefs.healthcare_weight + prefs.education_weight
    if total_weight == 0: total_weight = 1
        
    scored_candidates = []
    
    for cand in candidates:
        loc = cand["db_obj"]
        est_mins = cand["est_mins"]
        
        reasons = []
        tradeoffs = []
        
        # --- 2. FEATURE ENGINEERING ---
        feature_vector = extract_features(loc)
        
        # --- 3. ML PREDICTIONS ---
        ml_score = predict_suitability(prefs, feature_vector)
        
        # --- 4. PERSONALIZED SCORING (Ensemble) ---
        base_score = 0.0
        
        # Rent
        if loc.avg_rent <= prefs.budget * 0.8:
            reasons.append("Comfortably within your rent budget")
        else:
            reasons.append("Meets your budget requirements")
            
        # Commute
        if est_mins is not None:
            if est_mins <= 20:
                reasons.append(f"Ultra-short predicted commute ({est_mins} mins)")
            elif est_mins > prefs.max_commute_minutes * 0.8:
                tradeoffs.append(f"Pushing your commute limits ({est_mins} mins)")
            else:
                reasons.append(f"Reasonable commute ({est_mins} mins)")
        
        base_score += feature_vector.commute_normalized * prefs.commute_weight
        
        # Safety
        if loc.safety_score and loc.safety_score >= 8:
            reasons.append("Excellent safety record")
        elif loc.safety_score and loc.safety_score < 6:
            tradeoffs.append("Safety score is lower than average")
        base_score += feature_vector.safety_normalized * prefs.safety_weight
        
        # AQI
        if loc.air_quality_index and loc.air_quality_index <= 50:
            reasons.append("Great air quality")
        elif loc.air_quality_index and loc.air_quality_index > 150:
            tradeoffs.append("Poor air quality/pollution")
        base_score += feature_vector.aqi_normalized * prefs.pollution_weight
        
        # Healthcare/Edu
        if feature_vector.healthcare_normalized > 0.8: reasons.append("Strong healthcare availability")
        if feature_vector.education_normalized > 0.8: reasons.append("Excellent school density")
        
        base_score += feature_vector.healthcare_normalized * prefs.healthcare_weight
        base_score += feature_vector.education_normalized * prefs.education_weight
        
        # Combine Base Score (Deterministic) and ML Score
        deterministic_score = base_score / total_weight
        
        # Final Ensemble: 60% Deterministic, 40% ML
        final_score = (deterministic_score * 0.6) + (ml_score * 0.4)
        
        response_item = RecommendationResponseItem(
            locality=loc.name,
            locality_id=loc.id,
            city_id=loc.city_id,
            city_name=loc.city.name if loc.city else "Unknown",
            final_score=round(final_score, 3),
            ml_suitability=round(ml_score, 3),
            constraint_status="eligible",
            predicted_commute_minutes=est_mins,
            predicted_rent=loc.avg_rent or 0,
            safety_score=loc.safety_score or 0.0,
            air_quality_score=loc.air_quality_index or 0.0,
            reasons=reasons,
            tradeoffs=tradeoffs
        )
        scored_candidates.append(response_item)
        
    # --- 5. FORECASTING & FINAL RANKING ---
    scored_candidates.sort(key=lambda x: x.final_score, reverse=True)
    top_candidates = scored_candidates[:5]
    
    final_recommendations = []
    
    for cand in top_candidates:
        hist_data = db.query(HistoricalDataDB)\
            .filter(HistoricalDataDB.locality_id == cand.locality_id)\
            .order_by(HistoricalDataDB.month_year.asc())\
            .all()
            
        if hist_data and len(hist_data) >= 12:
            forecast = train_and_forecast(hist_data, months_ahead=6)
            
            if forecast:
                # ML Feature 3: Rent Trend Prediction
                future_rent = forecast[-1]['forecast_rent']
                if future_rent > prefs.budget:
                    cand.tradeoffs.append("Predicted to exceed your rent budget within 6 months")
                    cand.final_score *= 0.95 # Slight penalty
                    
                # ML Feature 4: Air Quality Forecast
                future_aqis = [f['forecast_aqi'] for f in forecast]
                avg_future_aqi = sum(future_aqis) / len(future_aqis)
                if avg_future_aqi > 200:
                    cand.tradeoffs.append("Forecasted to have severe winter smog spikes")
                    cand.final_score *= 0.90 # High penalty for severe pollution
            
            # ML Feature 7: Anomaly Detection
            from ml.models.anomaly import detect_anomalies
            is_anomaly, anomaly_alerts = detect_anomalies(hist_data, cand.predicted_rent, cand.air_quality_score)
            if is_anomaly:
                cand.is_anomaly = True
                cand.anomaly_alerts = anomaly_alerts
                cand.final_score *= 0.85 # Strong penalty for active anomalies
        
        # Round final score again
        cand.final_score = round(cand.final_score, 3)
        final_recommendations.append(cand)
        
    final_recommendations.sort(key=lambda x: x.final_score, reverse=True)
    return final_recommendations[:3]

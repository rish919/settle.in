from sqlalchemy.orm import Session
from datetime import datetime
from models.alerts import AlertCheckRequest, SmartAlert
from models.db_models import LocalityDB, HistoricalDataDB
from ml.models.anomaly import detect_anomalies
from ml.forecaster import train_and_forecast
from typing import List

def check_for_alerts(db: Session, request: AlertCheckRequest) -> List[SmartAlert]:
    alerts = []
    
    for loc_id in request.locality_ids:
        loc = db.query(LocalityDB).filter(LocalityDB.id == loc_id).first()
        if not loc:
            continue
            
        city_name = loc.city.name if loc.city else "Unknown City"
        
        hist_data = db.query(HistoricalDataDB)\
            .filter(HistoricalDataDB.locality_id == loc_id)\
            .order_by(HistoricalDataDB.month_year.asc())\
            .all()
            
        if not hist_data or len(hist_data) < 12:
            continue
            
        # 1. Anomaly Detection
        is_anomaly, anomaly_messages = detect_anomalies(hist_data, loc.avg_rent, loc.air_quality_index)
        
        if is_anomaly:
            for msg in anomaly_messages:
                alerts.append(SmartAlert(
                    id=f"anomaly_{loc_id}_{datetime.now().strftime('%Y%m%d')}",
                    type="anomaly",
                    locality_id=loc_id,
                    locality_name=loc.name,
                    city_name=city_name,
                    message=msg,
                    severity="critical",
                    timestamp=datetime.now()
                ))
                
        # 2. Forecast Breaches
        forecasts = train_and_forecast(hist_data, months_ahead=6)
        if forecasts:
            # Check if rent exceeds budget in the future
            if request.max_rent:
                breach_month = None
                for f in forecasts:
                    if f["forecast_rent"] > request.max_rent:
                        breach_month = f["month_year"]
                        break
                
                if breach_month:
                    alerts.append(SmartAlert(
                        id=f"forecast_rent_{loc_id}_{breach_month}",
                        type="forecast",
                        locality_id=loc_id,
                        locality_name=loc.name,
                        city_name=city_name,
                        message=f"Rent is forecasted to exceed your ₹{request.max_rent:,} budget by {breach_month}. Lock in a lease now.",
                        severity="warning",
                        timestamp=datetime.now()
                    ))
            
            # Check for severe AQI in the future
            severe_aqi_month = None
            peak_aqi = 0
            for f in forecasts:
                if f["forecast_aqi"] > 250:
                    severe_aqi_month = f["month_year"]
                    peak_aqi = max(peak_aqi, f["forecast_aqi"])
                    
            if severe_aqi_month:
                alerts.append(SmartAlert(
                    id=f"forecast_aqi_{loc_id}_{severe_aqi_month}",
                    type="forecast",
                    locality_id=loc_id,
                    locality_name=loc.name,
                    city_name=city_name,
                    message=f"Severe winter smog (AQI ~{peak_aqi}) is predicted around {severe_aqi_month}.",
                    severity="warning",
                    timestamp=datetime.now()
                ))
                
    return alerts

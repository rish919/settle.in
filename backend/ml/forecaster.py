import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from typing import List, Dict, Any
import datetime

def train_and_forecast(historical_data: List[Any], months_ahead: int = 6) -> List[Dict[str, Any]]:
    """
    Trains ML models on historical time-series data to forecast future trends.
    Rent: LinearRegression (good for long-term linear trends/inflation).
    AQI: RandomForestRegressor with Cyclical Feature Encoding (captures seasonal winter smog).
    """
    if not historical_data or len(historical_data) < 12:
        return []
        
    X_time = []
    X_cyclical = []
    
    # historical_data is ordered chronologically
    for i, d in enumerate(historical_data):
        # Extract month from "YYYY-MM"
        dt = datetime.datetime.strptime(d.month_year, "%Y-%m")
        month = dt.month
        
        # Cyclical encoding for month
        sin_m = np.sin(2 * np.pi * month / 12)
        cos_m = np.cos(2 * np.pi * month / 12)
        
        X_time.append([i])
        X_cyclical.append([i, sin_m, cos_m])
        
    X_time = np.array(X_time)
    X_cyclical = np.array(X_cyclical)
    
    y_rent = np.array([d.rent for d in historical_data])
    y_aqi = np.array([d.aqi for d in historical_data])
    
    # Train models
    lr_rent = LinearRegression()
    rf_aqi = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    
    lr_rent.fit(X_time, y_rent)
    rf_aqi.fit(X_cyclical, y_aqi)
    
    # Predict future
    last_idx = len(historical_data)
    last_dt = datetime.datetime.strptime(historical_data[-1].month_year, "%Y-%m")
    
    forecasts = []
    for i in range(months_ahead):
        future_idx = last_idx + i
        
        # Calculate future month
        future_m = last_dt.month + i + 1
        future_y = last_dt.year
        while future_m > 12:
            future_m -= 12
            future_y += 1
            
        month_str = f"{future_y}-{future_m:02d}"
        
        sin_m = np.sin(2 * np.pi * future_m / 12)
        cos_m = np.cos(2 * np.pi * future_m / 12)
        
        pred_rent = lr_rent.predict([[future_idx]])[0]
        pred_aqi = rf_aqi.predict([[future_idx, sin_m, cos_m]])[0]
        
        forecasts.append({
            "month_offset": i + 1,
            "month_year": month_str,
            "forecast_rent": int(pred_rent),
            "forecast_aqi": int(pred_aqi)
        })
        
    return forecasts

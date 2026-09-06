import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any, Tuple

def detect_anomalies(historical_data: List[Any], current_rent: float, current_aqi: float) -> Tuple[bool, List[str]]:
    """
    Uses IsolationForest to detect if the current metrics (rent, aqi)
    are anomalies compared to the locality's historical data.
    """
    if not historical_data or len(historical_data) < 12:
        return False, []
        
    # Prepare training data (historical)
    X_train = np.array([[d.rent, d.aqi] for d in historical_data])
    
    # Train Isolation Forest
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(X_train)
    
    # Predict current
    X_current = np.array([[current_rent, current_aqi]])
    prediction = clf.predict(X_current)
    
    is_anomaly = prediction[0] == -1
    alerts = []
    
    if is_anomaly:
        # Determine why it's an anomaly using simple Z-scores as explanation
        rent_mean = np.mean(X_train[:, 0])
        rent_std = np.std(X_train[:, 0])
        aqi_mean = np.mean(X_train[:, 1])
        aqi_std = np.std(X_train[:, 1])
        
        if current_rent > rent_mean + 1.5 * rent_std:
            alerts.append(f"Rent has spiked unusually high (₹{int(current_rent):,}) compared to the historical average (₹{int(rent_mean):,}).")
        elif current_rent < rent_mean - 1.5 * rent_std:
            alerts.append(f"Rent is unusually low (₹{int(current_rent):,}) compared to historical average.")
            
        if current_aqi > aqi_mean + 1.5 * aqi_std:
            alerts.append(f"Air quality is significantly worse ({int(current_aqi)}) than historical average ({int(aqi_mean)}).")
            
        if not alerts:
            alerts.append("Unusual conditions detected compared to historical trends.")
            
    return is_anomaly, alerts

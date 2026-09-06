import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'baseline_rf.pkl')

def train_synthetic_model():
    """
    Trains a baseline Random Forest model on a synthetic dataset.
    This serves as our initial ML Feature 1 (Suitability Prediction) 
    until we gather enough live user feedback to train on real interaction data.
    """
    print("Generating synthetic user-locality interactions...")
    np.random.seed(42)
    
    # Generate 5000 random user profiles (weights)
    n_samples = 5000
    user_rent_w = np.random.uniform(0, 1, n_samples)
    user_aqi_w = np.random.uniform(0, 1, n_samples)
    user_safety_w = np.random.uniform(0, 1, n_samples)
    user_commute_w = np.random.uniform(0, 1, n_samples)
    user_health_w = np.random.uniform(0, 1, n_samples)
    user_edu_w = np.random.uniform(0, 1, n_samples)
    
    # Generate 5000 random locality feature vectors
    loc_rent = np.random.uniform(0, 1, n_samples)
    loc_aqi = np.random.uniform(0, 1, n_samples)
    loc_safety = np.random.uniform(0, 1, n_samples)
    loc_commute = np.random.uniform(0, 1, n_samples)
    loc_health = np.random.uniform(0, 1, n_samples)
    loc_edu = np.random.uniform(0, 1, n_samples)
    
    # Target (Suitability): We create a slightly noisy synthetic "true" suitability
    # where the user's weights multiplied by the locality features dictate the score.
    # We add some non-linear synergy (e.g., high safety + high health is extra good)
    
    base_score = (
        (user_rent_w * loc_rent) +
        (user_aqi_w * loc_aqi) +
        (user_safety_w * loc_safety) +
        (user_commute_w * loc_commute) +
        (user_health_w * loc_health) +
        (user_edu_w * loc_edu)
    )
    
    # Normalize base score roughly
    max_possible_weight = user_rent_w + user_aqi_w + user_safety_w + user_commute_w + user_health_w + user_edu_w
    suitability = base_score / (max_possible_weight + 0.0001)
    
    # Add non-linear synergy noise
    synergy = (loc_safety * loc_health) * 0.1
    suitability += synergy
    suitability = np.clip(suitability, 0.0, 1.0)
    
    # Combine into X
    X = np.column_stack((
        user_rent_w, user_aqi_w, user_safety_w, user_commute_w, user_health_w, user_edu_w,
        loc_rent, loc_aqi, loc_safety, loc_commute, loc_health, loc_edu
    ))
    y = suitability
    
    print("Training baseline Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
    model.fit(X, y)
    
    print(f"Saving model to {MODEL_PATH}")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("Done!")

if __name__ == "__main__":
    train_synthetic_model()

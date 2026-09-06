import os
import joblib
import numpy as np
from models.recommendation import UserProfile, LocalityFeatureVector

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'baseline_rf.pkl')

# Lazy load model
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            return None
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_suitability(user: UserProfile, loc_features: LocalityFeatureVector) -> float:
    """
    Given a UserProfile and a LocalityFeatureVector, returns an ML suitability score (0.0 to 1.0).
    """
    model = get_model()
    if not model:
        # Fallback if model not trained
        return 0.5
        
    # Construct input vector exactly as trained
    X = np.array([[
        user.budget, # Placeholder, will be replaced below
        user.pollution_weight / 10.0,
        user.safety_weight / 10.0,
        user.commute_weight / 10.0,
        user.healthcare_weight / 10.0,
        user.education_weight / 10.0,
        loc_features.rent_normalized,
        loc_features.aqi_normalized,
        loc_features.safety_normalized,
        loc_features.commute_normalized,
        loc_features.healthcare_normalized,
        loc_features.education_normalized
    ]])
    
    # Actually wait, in `train_baseline.py`, the first column was `user_rent_w`.
    # Let's use lifestyle weight or budget as a proxy for rent weight.
    # We'll use 1.0 - (budget/150000) as the "importance of cheap rent".
    # Or we can just use `user.budget` but the model was trained on 0-1.
    rent_w = 1.0 if user.budget < 40000 else 0.5 
    
    X[0][0] = rent_w
    
    pred = model.predict(X)[0]
    return float(np.clip(pred, 0.0, 1.0))

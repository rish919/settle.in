from typing import Optional, List
from pydantic import BaseModel, Field, validator

class UserProfile(BaseModel):
    """Structured representation of the user preferences."""
    # Match frontend keys
    budget: int = Field(alias="max_rent", default=30000)
    max_commute_minutes: int = Field(alias="max_commute_mins", default=60)
    
    # Feature Importance Weights (Frontend sends 1-10, we want to scale to 0.0-1.0 if needed, or just use 1-10)
    # The prompt actually requested weights like 0.30, but the UI has 1-10 sliders. We will keep them as 0.0-10.0
    # and normalize them in the ML code.
    safety_weight: float = Field(default=5.0, ge=0.0, le=10.0)
    pollution_weight: float = Field(alias="aqi_weight", default=5.0, ge=0.0, le=10.0)
    commute_weight: float = Field(default=5.0, ge=0.0, le=10.0)
    
    # Optional ones not yet in frontend, defaulting to 5
    healthcare_weight: float = Field(default=5.0, ge=0.0, le=10.0)
    education_weight: float = Field(default=5.0, ge=0.0, le=10.0)
    lifestyle_weight: float = Field(default=5.0, ge=0.0, le=10.0)

    # Optional origin coordinates for commute constraints
    workplace_lat: Optional[float] = None
    workplace_lng: Optional[float] = None

    class Config:
        populate_by_name = True

class RecommendationRequest(BaseModel):
    """Payload for requesting locality recommendations."""
    profile: UserProfile

class LocalityFeatureVector(BaseModel):
    """Normalized locality features for ML inference."""
    rent_normalized: float
    aqi_normalized: float
    safety_normalized: float
    commute_normalized: float
    healthcare_normalized: float
    education_normalized: float

class RecommendationResponseItem(BaseModel):
    """Output schema for a single recommendation."""
    locality: str
    locality_id: str
    city_id: str
    city_name: str
    
    # Scores
    final_score: float = Field(description="Combined ensemble score (0.0 to 1.0)")
    ml_suitability: float = Field(description="Pure ML prediction score (0.0 to 1.0)")
    constraint_status: str = Field(default="eligible")
    
    # Metrics
    predicted_commute_minutes: Optional[int] = None
    predicted_rent: int
    safety_score: float
    air_quality_score: float
    
    # Explanations
    reasons: List[str]
    tradeoffs: List[str]
    is_anomaly: bool = False
    anomaly_alerts: List[str] = Field(default_factory=list)

class UserFeedbackRequest(BaseModel):
    """Payload for submitting feedback on a recommendation."""
    locality_id: str
    interaction_type: str # 'like', 'dislike', 'save', 'too_expensive', 'too_far'
    context_budget: Optional[int] = None
    context_commute_weight: Optional[float] = None


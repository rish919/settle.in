from typing import Optional
from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    """Payload for requesting locality recommendations."""
    max_rent: int = Field(default=100000, description="Maximum acceptable rent")
    safety_weight: int = Field(default=5, ge=1, le=10, description="Importance of safety (1-10)")
    commute_weight: int = Field(default=5, ge=1, le=10, description="Importance of commute score (1-10)")
    aqi_weight: int = Field(default=5, ge=1, le=10, description="Importance of air quality (1-10)")
    
    # Workplace Commute constraints
    workplace_lat: Optional[float] = None
    workplace_lng: Optional[float] = None
    max_commute_mins: int = Field(default=60, description="Maximum acceptable commute in minutes")
    
    # In a full app, we might also take 'city_id' to filter by a specific city, 
    # but for now we'll search across all localities in the mock data.

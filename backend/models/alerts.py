from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SmartAlert(BaseModel):
    id: str
    type: str  # "anomaly" | "forecast"
    locality_id: str
    locality_name: str
    city_name: str
    message: str
    severity: str  # "info" | "warning" | "critical"
    timestamp: datetime

class AlertCheckRequest(BaseModel):
    locality_ids: List[str]
    max_rent: Optional[int] = None
    max_commute_mins: Optional[int] = None
    # We can add more preferences here if needed

class AlertCheckResponse(BaseModel):
    alerts: List[SmartAlert]

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.alerts import AlertCheckRequest, AlertCheckResponse
from services.alert_service import check_for_alerts

router = APIRouter()

@router.post("/check", response_model=AlertCheckResponse)
def check_smart_alerts(request: AlertCheckRequest, db: Session = Depends(get_db)):
    """
    Evaluates saved localities for any ML anomalies or forecast breaches.
    Returns a list of SmartAlerts.
    """
    alerts = check_for_alerts(db, request)
    return AlertCheckResponse(alerts=alerts)

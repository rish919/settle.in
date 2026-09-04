from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.recommendation import RecommendationRequest
from services import recommendation_service
from database import get_db

router = APIRouter()

@router.post("")
def get_recommendations(prefs: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Get locality recommendations based on user preferences.
    """
    results = recommendation_service.get_recommendations(db, prefs)
    return results

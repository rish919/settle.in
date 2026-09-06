from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from models.recommendation import RecommendationRequest, RecommendationResponseItem, UserFeedbackRequest
from services import recommendation_service
from database import get_db

router = APIRouter()

@router.post("", response_model=List[RecommendationResponseItem])
def get_recommendations(prefs: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Get locality recommendations based on user preferences.
    """
    results = recommendation_service.get_recommendations(db, prefs)
    return results

@router.post("/feedback")
def submit_feedback(feedback: UserFeedbackRequest, db: Session = Depends(get_db)):
    """
    Log user interaction for future ML model retraining.
    """
    import datetime
    from models.db_models import UserInteractionDB
    
    db_interaction = UserInteractionDB(
        session_id="anonymous", # Later, hook this up to real auth
        locality_id=feedback.locality_id,
        interaction_type=feedback.interaction_type,
        timestamp=datetime.datetime.utcnow().isoformat(),
        context_budget=feedback.context_budget,
        context_commute_weight=feedback.context_commute_weight
    )
    
    db.add(db_interaction)
    db.commit()
    return {"status": "success"}

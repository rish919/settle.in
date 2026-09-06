"""
settle — Background Scheduler

Manages background tasks like daily AQI updates using APScheduler.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import asyncio
from database import SessionLocal
from models.db_models import LocalityDB
from services.environmental_service import fetch_current_aqi

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def update_all_aqi():
    """
    Background job to fetch and update AQI for all localities in the database.
    """
    logger.info("Starting scheduled AQI update job...")
    db = SessionLocal()
    try:
        localities = db.query(LocalityDB).all()
        updated_count = 0
        
        sem = asyncio.Semaphore(20) # Max 20 concurrent requests
        
        async def fetch_and_update(loc):
            async with sem:
                aqi = await fetch_current_aqi(loc.lat, loc.lng)
                return loc, aqi
                
        tasks = [fetch_and_update(loc) for loc in localities]
        results = await asyncio.gather(*tasks)
        
        for loc, aqi in results:
            if aqi is not None:
                loc.air_quality_index = aqi
                updated_count += 1
                
        db.commit()
        logger.info(f"Successfully updated AQI for {updated_count}/{len(localities)} localities.")
    except Exception as e:
        logger.error(f"Error during AQI update job: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Starts the APScheduler and adds jobs."""
    # Add daily AQI update job (e.g., at 2:00 AM)
    scheduler.add_job(
        update_all_aqi,
        CronTrigger(hour=2, minute=0),
        id="update_aqi_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started with jobs: [update_aqi_job]")

def shutdown_scheduler():
    """Shuts down the APScheduler."""
    scheduler.shutdown()
    logger.info("APScheduler shutdown.")

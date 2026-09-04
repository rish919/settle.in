"""
settle — Environmental Service

Fetches real-time AQI and Weather data using the Open-Meteo API.
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Open-Meteo Air Quality API base URL
AQI_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

async def fetch_current_aqi(lat: float, lng: float) -> Optional[int]:
    """
    Fetches the current US AQI for the given coordinates.
    """
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "us_aqi"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(AQI_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract the current US AQI
            current_aqi = data.get("current", {}).get("us_aqi")
            
            if current_aqi is not None:
                return int(current_aqi)
            else:
                logger.warning(f"AQI data not found in response for {lat},{lng}")
                return None
                
    except httpx.RequestError as e:
        logger.error(f"Error fetching AQI for {lat},{lng}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching AQI: {e}")
        return None

"""
settle — Trigger AQI Update Script
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduler import update_all_aqi

if __name__ == "__main__":
    asyncio.run(update_all_aqi())

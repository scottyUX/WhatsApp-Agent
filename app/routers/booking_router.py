"""
Booking Router for Polling-based Real-time Notifications
Compatible with Vercel's serverless architecture
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import time
import logging

log = logging.getLogger("booking_router")

router = APIRouter(
    prefix="/api",
    tags=["Booking"],
)

# In-memory storage for demo purposes
# In production, this would be a database
recent_bookings: List[Dict[str, Any]] = []

@router.get("/check-bookings/{user_id}")
async def check_bookings(
    user_id: str,
    since: int = Query(..., description="Timestamp to check bookings since")
):
    """Check for new bookings since a given timestamp"""
    try:
        current_time = int(time.time() * 1000)  # Current timestamp in milliseconds
        
        # Filter bookings that are newer than the 'since' timestamp
        new_bookings = [
            booking for booking in recent_bookings 
            if booking.get('timestamp', 0) > since
        ]
        
        # Sort by timestamp (newest first)
        new_bookings.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        log.info(f"📅 Checked bookings for user {user_id}: {len(new_bookings)} new bookings since {since}")
        
        return {
            "user_id": user_id,
            "bookings": new_bookings,
            "checked_at": current_time,
            "count": len(new_bookings)
        }
        
    except Exception as e:
        log.error(f"❌ Error checking bookings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check bookings")

@router.post("/add-booking")
async def add_booking(booking_data: Dict[str, Any]):
    """Add a new booking to the recent bookings list"""
    try:
        # Add timestamp to the booking
        booking_data['timestamp'] = int(time.time() * 1000)
        
        # Add to recent bookings
        recent_bookings.append(booking_data)
        
        # Keep only last 100 bookings to prevent memory issues
        if len(recent_bookings) > 100:
            recent_bookings.pop(0)
        
        log.info(f"📅 Added new booking: {booking_data.get('booking_id', 'Unknown')}")
        
        return {
            "status": "success",
            "message": "Booking added successfully",
            "booking_id": booking_data.get('booking_id'),
            "timestamp": booking_data['timestamp']
        }
        
    except Exception as e:
        log.error(f"❌ Error adding booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to add booking")

@router.get("/recent-bookings")
async def get_recent_bookings(limit: int = Query(10, description="Number of recent bookings to return")):
    """Get recent bookings for debugging"""
    return {
        "bookings": recent_bookings[-limit:],
        "total": len(recent_bookings),
        "timestamp": int(time.time() * 1000)
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, BookingEvent
from app.services.auth_service import get_current_user_id
from app.services.booking_service import (
    booking_exists,
    get_booking_history,
    list_bookings,
    replay_events,
)

router = APIRouter(prefix="/bookings", tags=["queries:bookings"])


@router.get("")
def get_all_bookings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> list[Booking]:
    """Query: list every booking belonging to the current user."""
    return list_bookings(db, user_id)


@router.get("/{booking_id}")
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> Booking:
    """Query: get the current state of a booking, rebuilt from its events."""
    if not booking_exists(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = replay_events(db, booking_id)
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your booking")
    return booking


@router.get("/{booking_id}/history")
def get_booking_events(
    booking_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> list[BookingEvent]:
    """Query: get the raw, immutable event log for a booking."""
    if not booking_exists(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = replay_events(db, booking_id)
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your booking")
    return get_booking_history(db, booking_id)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, BookingEvent
from app.services.booking_service import get_booking_history, list_bookings, replay_events

router = APIRouter(prefix="/bookings", tags=["queries:bookings"])


@router.get("")
def get_all_bookings(db: Session = Depends(get_db)) -> list[Booking]:
    """Query: list every booking, current state only."""
    return list_bookings(db)


@router.get("/{booking_id}")
def get_booking(booking_id: str, db: Session = Depends(get_db)) -> Booking:
    """Query: get the current state of a booking, rebuilt from its events."""
    return replay_events(db, booking_id)


@router.get("/{booking_id}/history")
def get_booking_events(booking_id: str, db: Session = Depends(get_db)) -> list[BookingEvent]:
    """Query: get the raw, immutable event log for a booking."""
    return get_booking_history(db, booking_id)
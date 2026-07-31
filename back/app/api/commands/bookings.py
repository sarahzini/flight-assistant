from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, BookingRequest
from app.services.auth_service import get_current_user_id
from app.services.booking_service import (
    booking_exists,
    cancel_booking,
    confirm_booking,
    create_booking,
    replay_events,
)

router = APIRouter(prefix="/bookings", tags=["commands:bookings"])


@router.post("")
def post_booking(
    request: BookingRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> Booking:
    """Command: create a new booking, owned by the current user."""
    return create_booking(db, request, user_id)


@router.post("/{booking_id}/confirm")
def post_confirm(
    booking_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> Booking:
    """Command: confirm an existing booking, only if it belongs to the current user."""
    if not booking_exists(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = replay_events(db, booking_id)
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your booking")
    return confirm_booking(db, booking_id)


@router.post("/{booking_id}/cancel")
def post_cancel(
    booking_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> Booking:
    """Command: cancel an existing booking, only if it belongs to the current user."""
    if not booking_exists(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = replay_events(db, booking_id)
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your booking")
    return cancel_booking(db, booking_id)
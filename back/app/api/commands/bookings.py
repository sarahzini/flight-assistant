from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, BookingRequest
from app.services.booking_service import cancel_booking, confirm_booking, create_booking

router = APIRouter(prefix="/bookings", tags=["commands:bookings"])


@router.post("")
def post_booking(request: BookingRequest, db: Session = Depends(get_db)) -> Booking:
    return create_booking(db, request)


@router.post("/{booking_id}/confirm")
def post_confirm(booking_id: str, db: Session = Depends(get_db)) -> Booking:
    return confirm_booking(db, booking_id)


@router.post("/{booking_id}/cancel")
def post_cancel(booking_id: str, db: Session = Depends(get_db)) -> Booking:
    return cancel_booking(db, booking_id)
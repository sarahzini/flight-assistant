import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.db_models import BookingEventRow
from app.models import Booking, BookingEvent, BookingRequest, BookingStatus


def _append_event(db: Session, event_type: str, booking_id: str, data: dict) -> None:
    """Store one immutable event row. This is the only way state ever changes."""
    row = BookingEventRow(
        booking_id=booking_id,
        event_type=event_type,
        timestamp=datetime.utcnow(),
        data=data,
    )
    db.add(row)
    db.commit()


def create_booking(db: Session, request: BookingRequest) -> Booking:
    booking_id = str(uuid.uuid4())
    _append_event(
        db,
        event_type="BookingCreated",
        booking_id=booking_id,
        data={
            "flight_number": request.flight_number,
            "passenger_name": request.passenger_name,
        },
    )
    return replay_events(db, booking_id)


def confirm_booking(db: Session, booking_id: str) -> Booking:
    _append_event(db, event_type="BookingConfirmed", booking_id=booking_id, data={})
    return replay_events(db, booking_id)


def cancel_booking(db: Session, booking_id: str) -> Booking:
    _append_event(db, event_type="BookingCancelled", booking_id=booking_id, data={})
    return replay_events(db, booking_id)


def replay_events(db: Session, booking_id: str) -> Booking:
    """Query: rebuild current state by replaying every event for this booking, in timestamp order."""
    rows = (
        db.query(BookingEventRow)
        .filter(BookingEventRow.booking_id == booking_id)
        .order_by(BookingEventRow.timestamp)
        .all()
    )

    state = {
        "booking_id": booking_id,
        "flight_number": None,
        "passenger_name": None,
        "status": BookingStatus.CREATED,
    }

    for row in rows:
        if row.event_type == "BookingCreated":
            state["flight_number"] = row.data["flight_number"]
            state["passenger_name"] = row.data["passenger_name"]
            state["status"] = BookingStatus.CREATED
        elif row.event_type == "BookingConfirmed":
            state["status"] = BookingStatus.CONFIRMED
        elif row.event_type == "BookingCancelled":
            state["status"] = BookingStatus.CANCELLED

    return Booking(**state)

def list_bookings(db: Session) -> list[Booking]:
    """Query: list all bookings, each rebuilt from its own event history."""
    booking_ids = db.query(BookingEventRow.booking_id).distinct().all()
    return [replay_events(db, row[0]) for row in booking_ids]


def get_booking_history(db: Session, booking_id: str) -> list[BookingEvent]:
    """Query: return the raw, unmodified event log for a booking — not the replayed state."""
    rows = (
        db.query(BookingEventRow)
        .filter(BookingEventRow.booking_id == booking_id)
        .order_by(BookingEventRow.timestamp)
        .all()
    )
    return [
        BookingEvent(
            event_type=row.event_type,
            booking_id=row.booking_id,
            timestamp=row.timestamp,
            data=row.data,
        )
        for row in rows
    ]
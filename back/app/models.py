from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Airport(BaseModel):
    name: str
    iata: str
    scheduled_time: str
    terminal: Optional[str] = None
    gate: Optional[str] = None
    delay: Optional[int] = None


class Airline(BaseModel):
    name: str
    iata: str


class Flight(BaseModel):
    flight_date: str
    flight_status: str
    flight_number: str
    airline: Airline
    departure: Airport
    arrival: Airport

class AdvisorQuery(BaseModel):
    question: str


class AdvisorAnswer(BaseModel):
    answer: str
    sources: list[str] = []

class BookingStatus(str, Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingRequest(BaseModel):
    """Input from the user — Command side."""
    flight_number: str
    passenger_name: str


class BookingEvent(BaseModel):
    """A single event stored in the event log."""
    event_type: str
    booking_id: str
    timestamp: datetime
    data: dict


class Booking(BaseModel):
    """Reconstructed state — Query side, rebuilt by replaying events."""
    booking_id: str
    flight_number: str
    passenger_name: str
    status: BookingStatus


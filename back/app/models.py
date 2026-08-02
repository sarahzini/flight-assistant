from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

#Models for the flights API

class Airport(BaseModel):
    name: str | None = None
    iata: str | None = None
    scheduled_time: str | None = None
    terminal: Optional[str] = None
    gate: Optional[str] = None
    delay: Optional[int] = None


class Airline(BaseModel):
    name: str | None = None
    iata: str | None = None

class Flight(BaseModel):
    flight_date: str | None = None
    flight_status: str | None = None
    flight_number: str | None = None
    airline: Airline | None = None
    departure: Airport | None = None
    arrival: Airport | None = None

class AdvisorQuery(BaseModel):
    question: str


class AdvisorAnswer(BaseModel):
    answer: str
    sources: list[str] = []


#Models for the bookings API

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
    user_id: Optional[str] = None


#Models for the authentication API

class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
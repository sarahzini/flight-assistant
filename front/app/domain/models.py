from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


@dataclass
class Airport:
    name: str
    iata: str
    scheduled_time: str
    terminal: Optional[str] = None
    gate: Optional[str] = None
    delay: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Airport:
        return cls(
            name=data.get("name") or "",
            iata=data.get("iata") or "",
            scheduled_time=data.get("scheduled_time") or "",
            terminal=data.get("terminal"),
            gate=data.get("gate"),
            delay=data.get("delay"),
        )


@dataclass
class Airline:
    name: Optional[str] = None
    iata: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Airline:
        return cls(name=data.get("name"), iata=data.get("iata"))


@dataclass
class Flight:
    flight_date: str
    flight_status: str
    flight_number: str
    airline: Airline
    departure: Airport
    arrival: Airport

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Flight:
        airline_data = data.get("airline") or {}
        departure_data = data.get("departure") or {}
        arrival_data = data.get("arrival") or {}
        return cls(
            flight_date=data.get("flight_date") or "",
            flight_status=data.get("flight_status") or "",
            flight_number=data.get("flight_number") or "",
            airline=Airline.from_dict(airline_data),
            departure=Airport.from_dict(departure_data),
            arrival=Airport.from_dict(arrival_data),
        )


class BookingStatus(str, Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class BookingRequest:
    flight_number: str
    passenger_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "flight_number": self.flight_number,
            "passenger_name": self.passenger_name,
        }


@dataclass
class BookingEvent:
    event_type: str
    booking_id: str
    timestamp: datetime
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BookingEvent:
        ts = data["timestamp"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return cls(
            event_type=data["event_type"],
            booking_id=data["booking_id"],
            timestamp=ts,
            data=data.get("data", {}),
        )


@dataclass
class Booking:
    booking_id: str
    flight_number: str
    passenger_name: str
    status: BookingStatus
    user_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Booking:
        return cls(
            booking_id=data["booking_id"],
            flight_number=data["flight_number"],
            passenger_name=data["passenger_name"],
            status=BookingStatus(data["status"]),
            user_id=data.get("user_id"),
        )


@dataclass
class UserOut:
    id: str
    email: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserOut:
        return cls(id=data["id"], email=data["email"])


@dataclass
class Token:
    access_token: str
    token_type: str = "bearer"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Token:
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
        )


@dataclass
class AdvisorAnswer:
    answer: str
    sources: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AdvisorAnswer:
        return cls(answer=data["answer"], sources=data.get("sources", []))

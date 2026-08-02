from __future__ import annotations

from app.api.client import ApiClient
from app.domain.models import Booking, BookingEvent, BookingRequest


def list_bookings(client: ApiClient) -> list[Booking]:
    data = client.get("/bookings")
    return [Booking.from_dict(item) for item in data]


def get_booking(client: ApiClient, booking_id: str) -> Booking:
    data = client.get(f"/bookings/{booking_id}")
    return Booking.from_dict(data)


def get_booking_history(client: ApiClient, booking_id: str) -> list[BookingEvent]:
    data = client.get(f"/bookings/{booking_id}/history")
    return [BookingEvent.from_dict(item) for item in data]


def create_booking(client: ApiClient, request: BookingRequest) -> Booking:
    data = client.post("/bookings", json=request.to_dict())
    return Booking.from_dict(data)


def confirm_booking(client: ApiClient, booking_id: str) -> Booking:
    data = client.post(f"/bookings/{booking_id}/confirm")
    return Booking.from_dict(data)


def cancel_booking(client: ApiClient, booking_id: str) -> Booking:
    data = client.post(f"/bookings/{booking_id}/cancel")
    return Booking.from_dict(data)

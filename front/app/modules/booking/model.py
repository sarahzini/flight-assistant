from __future__ import annotations

from app.api import bookings as bookings_api
from app.api.client import ApiClient
from app.domain.models import Booking, BookingRequest


class BookingModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_bookings(self) -> list[Booking]:
        return bookings_api.list_bookings(self._client)

    def create(self, flight_number: str, passenger_name: str) -> Booking:
        request = BookingRequest(flight_number=flight_number, passenger_name=passenger_name)
        return bookings_api.create_booking(self._client, request)

    def confirm(self, booking_id: str) -> Booking:
        return bookings_api.confirm_booking(self._client, booking_id)

    def cancel(self, booking_id: str) -> Booking:
        return bookings_api.cancel_booking(self._client, booking_id)

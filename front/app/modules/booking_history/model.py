from __future__ import annotations

from app.api import bookings as bookings_api
from app.api.client import ApiClient
from app.domain.models import BookingEvent


class BookingHistoryModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_history(self, booking_id: str) -> list[BookingEvent]:
        return bookings_api.get_booking_history(self._client, booking_id)
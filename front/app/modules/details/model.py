from __future__ import annotations

from app.api import flights as flights_api
from app.api.client import ApiClient
from app.domain.models import Flight


class DetailsModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_details(self, flight_iata: str) -> Flight:
        return flights_api.get_flight_details(self._client, flight_iata)

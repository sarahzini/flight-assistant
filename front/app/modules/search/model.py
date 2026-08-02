from __future__ import annotations

from app.api import flights as flights_api
from app.api.client import ApiClient
from app.domain.models import Flight


class SearchModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def search(self, dep_iata: str, limit: int) -> list[Flight]:
        return flights_api.search_flights(self._client, dep_iata=dep_iata, limit=limit)

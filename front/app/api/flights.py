from __future__ import annotations

from app.api.client import ApiClient
from app.domain.models import Flight


def search_flights(client: ApiClient, dep_iata: str, limit: int = 5) -> list[Flight]:
    data = client.get("/flights", params={"dep_iata": dep_iata, "limit": limit})
    return [Flight.from_dict(item) for item in data]


def get_flight_details(client: ApiClient, flight_iata: str) -> Flight:
    data = client.get(f"/flights/{flight_iata}")
    return Flight.from_dict(data)

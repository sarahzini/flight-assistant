import httpx

from app.config import AVIATIONSTACK_API_KEY
from app.models import Airline, Airport, Flight

AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"


def fetch_flights(dep_iata: str = None, limit: int = 5) -> dict:
    """Call the AviationStack flights endpoint and return the raw JSON response."""
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "limit": limit,
    }
    if dep_iata:
        params["dep_iata"] = dep_iata

    response = httpx.get(f"{AVIATIONSTACK_BASE_URL}/flights", params=params)
    response.raise_for_status()
    return response.json()

def parse_flight(raw: dict) -> Flight:
    """Convert a raw AviationStack flight dict into our Flight model."""
    return Flight(
        flight_date=raw["flight_date"],
        flight_status=raw["flight_status"],
        flight_number=raw["flight"]["iata"],
        airline=Airline(
            name=raw["airline"]["name"],
            iata=raw["airline"]["iata"],
        ),
        departure=Airport(
            name=raw["departure"]["airport"],
            iata=raw["departure"]["iata"],
            scheduled_time=raw["departure"]["scheduled"],
            terminal=raw["departure"]["terminal"],
            gate=raw["departure"]["gate"],
            delay=raw["departure"]["delay"],
        ),
        arrival=Airport(
            name=raw["arrival"]["airport"],
            iata=raw["arrival"]["iata"],
            scheduled_time=raw["arrival"]["scheduled"],
            terminal=raw["arrival"]["terminal"],
            gate=raw["arrival"]["gate"],
            delay=raw["arrival"]["delay"],
        ),
    )
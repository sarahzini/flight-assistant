from fastapi import APIRouter

from app.gateway import fetch_flights, parse_flight

router = APIRouter(prefix="/flights", tags=["queries:flights"])


@router.get("")
def search_flights(dep_iata: str, limit: int = 5):
    """Query: search flights departing from a given airport."""
    raw_data = fetch_flights(dep_iata=dep_iata, limit=limit)
    return [parse_flight(item) for item in raw_data["data"]]
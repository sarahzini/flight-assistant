from fastapi import APIRouter, HTTPException

from app.gateway import fetch_flights, parse_flight

router = APIRouter(prefix="/flights", tags=["queries:flights"])


@router.get("")
def search_flights(dep_iata: str, limit: int = 5):
    """Query: search flights departing from a given airport."""
    raw_data = fetch_flights(dep_iata=dep_iata, limit=limit)
    return [parse_flight(item) for item in raw_data["data"]]

@router.get("/{flight_iata}")
def get_flight_details(flight_iata: str):
    """Query: get details for one specific flight by its IATA code (e.g. LY4257)."""
    raw_data = fetch_flights(flight_iata=flight_iata, limit=1)
    if not raw_data["data"]:
        raise HTTPException(status_code=404, detail="Flight not found")
    return parse_flight(raw_data["data"][0])
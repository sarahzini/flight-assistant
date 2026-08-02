import httpx

from app.config import AVIATIONSTACK_API_KEY
from app.models import Airline, Airport, Flight

AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"

def fetch_flights(dep_iata: str = None, flight_iata: str = None, limit: int = 5) -> dict:
    """Call the AviationStack flights endpoint and return the raw JSON response."""
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "limit": limit,
    }
    if dep_iata:
        params["dep_iata"] = dep_iata
    if flight_iata:
        params["flight_iata"] = flight_iata

    response = httpx.get(f"{AVIATIONSTACK_BASE_URL}/flights", params=params)
    response.raise_for_status()
    return response.json()

def parse_flight(raw: dict) -> Flight:
    """Convert a raw AviationStack flight dict into our Flight model."""
    airline_raw = raw.get("airline") or {}
    flight_raw = raw.get("flight") or {}
    departure_raw = raw.get("departure") or {}
    arrival_raw = raw.get("arrival") or {}

    return Flight(
        flight_date=raw.get("flight_date"),
        flight_status=raw.get("flight_status"),
        flight_number=flight_raw.get("iata"),
        airline=Airline(
            name=airline_raw.get("name"),
            iata=airline_raw.get("iata"),
        ),
        departure=Airport(
            name=departure_raw.get("airport"),
            iata=departure_raw.get("iata"),
            scheduled_time=departure_raw.get("scheduled"),
            terminal=departure_raw.get("terminal"),
            gate=departure_raw.get("gate"),
            delay=departure_raw.get("delay"),
        ),
        arrival=Airport(
            name=arrival_raw.get("airport"),
            iata=arrival_raw.get("iata"),
            scheduled_time=arrival_raw.get("scheduled"),
            terminal=arrival_raw.get("terminal"),
            gate=arrival_raw.get("gate"),
            delay=arrival_raw.get("delay"),
        ),
    )

def fetch_embedding(text: str) -> list[float]:
    """Turn a piece of text into a vector of numbers representing its meaning."""
    response = httpx.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def fetch_advisor_completion(prompt: str) -> str:
    """Ask the LLM to generate a text answer for a given prompt."""
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 280,
            },
        },
        timeout=90,
    )
    response.raise_for_status()
    return response.json()["response"]
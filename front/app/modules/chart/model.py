from __future__ import annotations

from collections import defaultdict

from app.domain.models import Flight


def _airline_label(flight: Flight) -> str:
    if flight.airline:
        if flight.airline.name:
            return flight.airline.name
        if flight.airline.iata:
            return flight.airline.iata
    return "Unknown airline"


def count_by_airline(flights: list[Flight]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for flight in flights:
        counts[_airline_label(flight)] += 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def count_by_status(flights: list[Flight]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for flight in flights:
        status = (flight.flight_status or "unknown").strip().lower()
        counts[status] += 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def avg_departure_delay_by_airline(flights: list[Flight]) -> dict[str, float]:
    totals: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    for flight in flights:
        label = _airline_label(flight)
        delay = 0
        if flight.departure and flight.departure.delay is not None:
            delay = flight.departure.delay
        totals[label] += delay
        counts[label] += 1
    return {
        label: totals[label] / counts[label]
        for label in sorted(counts, key=lambda k: totals[k] / counts[k], reverse=True)
    }


def has_any_delay(flights: list[Flight]) -> bool:
    for flight in flights:
        if flight.departure and flight.departure.delay:
            return True
        if flight.arrival and flight.arrival.delay:
            return True
    return False

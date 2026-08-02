from __future__ import annotations

from typing import Optional

from app.domain.models import Flight


class AppState:
    """Cross-module shared state (selected flight, last search results)."""

    def __init__(self) -> None:
        self.selected_flight: Optional[Flight] = None
        self.search_results: list[Flight] = []

    def set_search_results(self, flights: list[Flight]) -> None:
        self.search_results = flights

    def set_selected_flight(self, flight: Optional[Flight]) -> None:
        self.selected_flight = flight

    def clear(self) -> None:
        self.selected_flight = None
        self.search_results = []

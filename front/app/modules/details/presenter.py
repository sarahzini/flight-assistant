from __future__ import annotations

from PySide6.QtCore import QObject

from app.api.client import error_message
from app.domain.models import Flight
from app.modules.details.model import DetailsModel
from app.modules.details.view import FlightDetailsPanel
from app.shared.app_state import AppState
from app.shared.async_worker import AsyncTaskRunner


class DetailsPresenter(QObject, AsyncTaskRunner):
    def __init__(self, view: FlightDetailsPanel, model: DetailsModel, app_state: AppState) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._app_state = app_state

        view.refresh_clicked.connect(self._on_refresh)

    def refresh(self) -> None:
        flight = self._app_state.selected_flight
        self._view.clear_error()

        if flight is None:
            self._view.show_placeholder()
            return

        self._view.show_flight(flight)

    def _on_refresh(self) -> None:
        flight = self._app_state.selected_flight
        if flight is None or not flight.flight_number:
            self._view.show_placeholder()
            return

        flight_number = flight.flight_number
        self._view.clear_error()
        self._view.set_loading(True)

        self.run_async(
            lambda: self._model.get_details(flight_number),
            self._on_refresh_success,
            self._on_refresh_error,
        )

    def _on_refresh_success(self, updated: Flight) -> None:
        self._view.set_loading(False)
        self._app_state.set_selected_flight(updated)
        self._update_search_results(updated)
        self._view.show_flight(updated)

    def _on_refresh_error(self, exc: Exception) -> None:
        self._view.set_loading(False)
        self._view.set_error(error_message(exc))

    def _update_search_results(self, flight: Flight) -> None:
        results = self._app_state.search_results
        for index, item in enumerate(results):
            if item.flight_number == flight.flight_number:
                results[index] = flight
                break

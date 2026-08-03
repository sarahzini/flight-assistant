from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Signal

from app.api.client import ApiError, error_message
from app.domain.models import Booking
from app.modules.booking.model import BookingModel
from app.modules.booking.view import BookingView
from app.shared.app_state import AppState
from app.shared.async_worker import AsyncTaskRunner
from app.shared.session import Session


class BookingPresenter(QObject, AsyncTaskRunner):
    auth_expired = Signal()

    def __init__(
        self,
        view: BookingView,
        model: BookingModel,
        session: Session,
        app_state: AppState,
    ) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._session = session
        self._app_state = app_state

        view.create_clicked.connect(self._on_create)
        view.confirm_clicked.connect(self._on_confirm)
        view.cancel_clicked.connect(self._on_cancel)
        view.refresh_clicked.connect(self.refresh)

    def refresh(self) -> None:
        if not self._ensure_auth():
            return

        self._prefill_from_selection()
        self._view.clear_error()
        self._view.set_loading(True)

        self.run_async(self._model.list_bookings, self._on_list_success, self._on_error)

    def _on_list_success(self, bookings: list[Booking]) -> None:
        self._view.set_loading(False)
        self._view.populate_table(bookings)

    def _prefill_from_selection(self) -> None:
        flight = self._app_state.selected_flight
        if flight and flight.flight_number:
            self._view.set_flight_number(flight.flight_number)

    def _on_create(self) -> None:
        if not self._ensure_auth():
            return

        flight_number = self._view.get_flight_number()
        passenger_name = self._view.get_passenger_name()

        if not flight_number:
            self._view.set_error("Enter a flight number (select a flight in Search first).")
            return
        if not passenger_name:
            self._view.set_error("Enter the passenger name.")
            return

        self._view.clear_error()
        self._view.set_loading(True)

        def do_create() -> list[Booking]:
            self._model.create(flight_number, passenger_name)
            return self._model.list_bookings()

        self.run_async(do_create, self._on_create_success, self._on_error)

    def _on_create_success(self, bookings: list[Booking]) -> None:
        self._view.set_loading(False)
        self._view.clear_passenger()
        self._view.populate_table(bookings)
        self._view.set_status("Booking created")

    def _on_confirm(self, booking_id: str) -> None:
        self._run_command(lambda: self._model.confirm(booking_id), "Booking confirmed")

    def _on_cancel(self, booking_id: str) -> None:
        self._run_command(lambda: self._model.cancel(booking_id), "Booking cancelled")

    def _run_command(self, action: Callable[[], Booking], success_message: str) -> None:
        if not self._ensure_auth():
            return

        self._view.clear_error()
        self._view.set_loading(True)

        def do_run() -> list[Booking]:
            action()
            return self._model.list_bookings()

        def on_success(bookings: list[Booking]) -> None:
            self._view.set_loading(False)
            self._view.populate_table(bookings)
            self._view.set_status(success_message)

        self.run_async(do_run, on_success, self._on_error)

    def _ensure_auth(self) -> bool:
        if self._session.is_authenticated():
            return True
        self.auth_expired.emit()
        return False

    def _on_error(self, exc: Exception) -> None:
        self._view.set_loading(False)
        if isinstance(exc, ApiError) and exc.status_code == 401:
            self.auth_expired.emit()
            return
        self._view.set_error(error_message(exc))

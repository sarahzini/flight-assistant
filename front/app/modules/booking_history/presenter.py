from __future__ import annotations

from PySide6.QtCore import QObject

from app.api.client import error_message
from app.domain.models import BookingEvent
from app.modules.booking_history.model import BookingHistoryModel
from app.modules.booking_history.view import BookingHistoryPanel
from app.shared.async_worker import AsyncTaskRunner


class BookingHistoryPresenter(QObject, AsyncTaskRunner):
    def __init__(self, view: BookingHistoryPanel, model: BookingHistoryModel) -> None:
        super().__init__()
        self._view = view
        self._model = model

    def load(self, booking_id: str) -> None:
        self._view.clear_error()

        self.run_async(
            lambda: self._model.get_history(booking_id),
            lambda events: self._view.show_history(booking_id, events),
            self._on_error,
        )

    def _on_error(self, exc: Exception) -> None:
        self._view.set_error(error_message(exc))
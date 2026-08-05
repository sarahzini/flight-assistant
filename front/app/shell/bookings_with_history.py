"""Shell-level composition of the Booking and Booking History microfrontends,
mirroring app/shell/search_with_details.py."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from app.modules.booking.view import BookingView
from app.modules.booking_history.view import BookingHistoryPanel


class BookingsWithHistoryContainer(QWidget):
    def __init__(
        self,
        booking_view: BookingView,
        history_panel: BookingHistoryPanel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sizes_initialized = False

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(booking_view)
        self._splitter.addWidget(history_panel)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 0)
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)
        self._splitter.setHandleWidth(1)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._splitter)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._sizes_initialized and self.width() > 0:
            table_width = max(self.width() - BookingHistoryPanel.PANEL_WIDTH - 40, 200)
            self._splitter.setSizes([table_width, BookingHistoryPanel.PANEL_WIDTH])
            self._sizes_initialized = True
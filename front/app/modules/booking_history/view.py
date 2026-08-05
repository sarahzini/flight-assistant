from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import BookingEvent
from app.shared.theme import Color, ErrorLabel


class BookingHistoryPanel(QFrame):
    """Side panel showing the raw, immutable event log for a selected booking."""

    PANEL_WIDTH = 320

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("bookingHistoryPanel")
        self.setFixedWidth(self.PANEL_WIDTH)
        self._build_ui()
        self.show_placeholder()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame#bookingHistoryPanel {{
                background: {Color.WHITE};
                border-left: 1px solid {Color.SLATE_200};
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        self._heading = QLabel("Booking history")
        self._heading.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Color.INK};")

        self._placeholder = QLabel(
            'Click "History" on a booking row to see its full event log.'
        )
        self._placeholder.setWordWrap(True)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._placeholder.setStyleSheet(f"color: {Color.SLATE_500}; font-size: 12px;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 4, 0)
        self._content_layout.setSpacing(8)
        self._content_layout.addStretch()

        scroll.setWidget(self._content)
        self._content.hide()

        self._error_label = ErrorLabel()
        self._error_label.setStyleSheet(f"color: {Color.DANGER}; font-size: 12px;")

        outer.addWidget(self._heading)
        outer.addWidget(self._placeholder)
        outer.addWidget(scroll, stretch=1)
        outer.addWidget(self._error_label)

        self._scroll = scroll

    def show_placeholder(self) -> None:
        self._heading.setText("Booking history")
        self._placeholder.show()
        self._content.hide()
        self._scroll.hide()

    def show_history(self, booking_id: str, events: list[BookingEvent]) -> None:
        self._heading.setText(f"History — {booking_id}")

        # Remove previous event cards, keep the trailing stretch (last item).
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for event in events:
            self._content_layout.insertWidget(
                self._content_layout.count() - 1, self._build_event_card(event)
            )

        self._placeholder.hide()
        self._content.show()
        self._scroll.show()

    def _build_event_card(self, event: BookingEvent) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {Color.SLATE_50}; border: 1px solid {Color.SLATE_200}; "
            "border-radius: 8px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        header_row = QHBoxLayout()
        type_label = QLabel(event.event_type)
        type_label.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {Color.SLATE_700};")
        time_label = QLabel(event.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        time_label.setStyleSheet(f"font-size: 10px; color: {Color.SLATE_500};")
        header_row.addWidget(type_label)
        header_row.addStretch()
        header_row.addWidget(time_label)
        layout.addLayout(header_row)

        HIDDEN_FIELDS = {"user_id"}

        for key, value in event.data.items():
            if key in HIDDEN_FIELDS:
                continue
            row = QHBoxLayout()
            row.setSpacing(6)
            name = QLabel(str(key))
            name.setFixedWidth(90)
            name.setStyleSheet(f"color: {Color.SLATE_500}; font-size: 11px;")
            val = QLabel(str(value))
            val.setWordWrap(True)
            val.setStyleSheet(f"color: {Color.INK}; font-size: 11px;")
            row.addWidget(name)
            row.addWidget(val, stretch=1)
            layout.addLayout(row)

        return card

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()
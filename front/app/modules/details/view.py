from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Flight
from app.shared.theme import Color, ErrorLabel, GhostIconButton


class FlightDetailsPanel(QFrame):
    """Compact side panel for the flight selected in the search table."""

    refresh_clicked = Signal()

    PANEL_WIDTH = 320

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("flightDetailsPanel")
        self.setFixedWidth(self.PANEL_WIDTH)
        self._build_ui()
        self.show_placeholder()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame#flightDetailsPanel {{
                background: {Color.WHITE};
                border-left: 1px solid {Color.SLATE_200};
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        header = QHBoxLayout()
        self._heading = QLabel("Flight details")
        self._heading.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Color.INK};")

        self._refresh_button = GhostIconButton("↻")
        self._refresh_button.setToolTip("Refresh from API")
        self._refresh_button.clicked.connect(self.refresh_clicked.emit)
        self._refresh_button.hide()

        header.addWidget(self._heading)
        header.addStretch()
        header.addWidget(self._refresh_button)

        self._placeholder = QLabel(
            "Select a flight in the table to view airline, route, times, and delays."
        )
        self._placeholder.setWordWrap(True)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._placeholder.setStyleSheet(
            f"color: {Color.SLATE_500}; font-size: 12px; line-height: 1.4;"
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 4, 0)
        content_layout.setSpacing(10)

        summary = QGridLayout()
        summary.setHorizontalSpacing(8)
        summary.setVerticalSpacing(8)
        self._airline_value = self._add_summary_field(summary, 0, 0, "Airline")
        self._flight_number_value = self._add_summary_field(summary, 0, 1, "Flight")
        self._status_value = self._add_summary_field(summary, 1, 0, "Status")
        self._date_value = self._add_summary_field(summary, 1, 1, "Date")
        content_layout.addLayout(summary)

        self._departure_card = self._build_airport_block("Departure")
        self._arrival_card = self._build_airport_block("Arrival")
        content_layout.addWidget(self._departure_card)
        content_layout.addWidget(self._arrival_card)
        content_layout.addStretch()

        scroll.setWidget(self._content)
        self._content.hide()

        self._error_label = ErrorLabel()
        self._error_label.setStyleSheet(f"color: {Color.DANGER}; font-size: 12px;")

        outer.addLayout(header)
        outer.addWidget(self._placeholder)
        outer.addWidget(scroll, stretch=1)
        outer.addWidget(self._error_label)

        self._scroll = scroll

    def _add_summary_field(self, grid: QGridLayout, row: int, col: int, label: str) -> QLabel:
        box = QVBoxLayout()
        box.setSpacing(2)
        name = QLabel(label)
        name.setStyleSheet(f"color: {Color.SLATE_500}; font-size: 10px; text-transform: uppercase;")
        value = QLabel("—")
        value.setWordWrap(True)
        value.setStyleSheet(f"color: {Color.INK}; font-size: 13px; font-weight: 600;")
        box.addWidget(name)
        box.addWidget(value)
        grid.addLayout(box, row, col)
        return value

    def _build_airport_block(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {Color.SLATE_50}; border: 1px solid {Color.SLATE_200}; "
            "border-radius: 8px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        heading = QLabel(title)
        heading.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {Color.SLATE_700};")
        layout.addWidget(heading)

        fields: dict[str, QLabel] = {}
        for label in ("Airport", "IATA", "Scheduled", "Terminal", "Gate", "Delay"):
            row = QHBoxLayout()
            row.setSpacing(6)
            name = QLabel(label)
            name.setFixedWidth(64)
            name.setStyleSheet(f"color: {Color.SLATE_500}; font-size: 11px;")
            value = QLabel("—")
            value.setWordWrap(True)
            value.setStyleSheet(f"color: {Color.INK}; font-size: 11px;")
            row.addWidget(name)
            row.addWidget(value, stretch=1)
            layout.addLayout(row)
            fields[label] = value

        if title == "Departure":
            self._departure_fields = fields
        else:
            self._arrival_fields = fields

        return card

    def show_placeholder(self) -> None:
        self._heading.setText("Flight details")
        self._placeholder.show()
        self._content.hide()
        self._scroll.hide()
        self._refresh_button.hide()

    def show_flight(self, flight: Flight) -> None:
        airline = "—"
        if flight.airline:
            airline = flight.airline.name or flight.airline.iata or "—"

        flight_no = flight.flight_number or "—"
        self._heading.setText(flight_no)
        self._airline_value.setText(airline)
        self._flight_number_value.setText(flight_no)
        self._status_value.setText(flight.flight_status or "—")
        self._date_value.setText(flight.flight_date or "—")

        self._fill_airport_block(self._departure_fields, flight.departure)
        self._fill_airport_block(self._arrival_fields, flight.arrival)

        self._placeholder.hide()
        self._content.show()
        self._scroll.show()
        self._refresh_button.setVisible(bool(flight.flight_number))

    def _fill_airport_block(self, fields: dict[str, QLabel], airport) -> None:
        if airport is None:
            for value in fields.values():
                value.setText("—")
            return

        fields["Airport"].setText(airport.name or "—")
        fields["IATA"].setText(airport.iata or "—")
        fields["Scheduled"].setText(airport.scheduled_time or "—")
        fields["Terminal"].setText(airport.terminal or "—")
        fields["Gate"].setText(airport.gate or "—")
        if airport.delay is None:
            fields["Delay"].setText("—")
        else:
            fields["Delay"].setText(f"{airport.delay} min")

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()

    def set_loading(self, loading: bool) -> None:
        self._refresh_button.setDisabled(loading)


DetailsView = FlightDetailsPanel

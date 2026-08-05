from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Booking
from app.shared.theme import (
    DangerOutlineButton,
    ErrorLabel,
    PrimaryButton,
    SecondaryButton,
    StatusLabel,
    SuccessButton,
    field_label,
    input_style,
    page_subtitle,
    page_title,
    table_style,
)


class BookingView(QWidget):
    create_clicked = Signal()
    confirm_clicked = Signal(str)
    cancel_clicked = Signal(str)
    refresh_clicked = Signal()
    history_clicked = Signal(str)

    _COLUMNS = ("ID", "Flight", "Passenger", "Status", "Actions")
    ACTIONS_COLUMN_WIDTH = 270

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bookings: list[Booking] = []
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = page_title("Bookings")
        subtitle = page_subtitle(
            "Create a booking from a selected flight, then confirm or cancel"
        )

        form = QHBoxLayout()
        form.setSpacing(12)

        flight_box = QVBoxLayout()
        flight_box.setSpacing(4)
        flight_box.addWidget(field_label("Flight number"))
        self._flight_input = QLineEdit()
        self._flight_input.setPlaceholderText("e.g. LY4257")
        self._flight_input.setStyleSheet(input_style())
        flight_box.addWidget(self._flight_input)

        passenger_box = QVBoxLayout()
        passenger_box.setSpacing(4)
        passenger_box.addWidget(field_label("Passenger name"))
        self._passenger_input = QLineEdit()
        self._passenger_input.setPlaceholderText("Full name")
        self._passenger_input.setStyleSheet(input_style())
        passenger_box.addWidget(self._passenger_input)

        self._create_button = PrimaryButton("Create booking")
        self._refresh_button = SecondaryButton("Refresh list")

        form.addLayout(flight_box, stretch=1)
        form.addLayout(passenger_box, stretch=2)
        form.addWidget(self._create_button, alignment=Qt.AlignmentFlag.AlignBottom)
        form.addWidget(self._refresh_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self._error_label = ErrorLabel()
        self._status_label = StatusLabel()

        self._table = QTableWidget(0, len(self._COLUMNS))
        self._table.setHorizontalHeaderLabels(list(self._COLUMNS))
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(44)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # A fixed width (rather than ResizeToContents) avoids Qt under-sizing
        # this column and clipping the Confirm/Cancel/History button labels.
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(4, self.ACTIONS_COLUMN_WIDTH)
        self._table.setStyleSheet(table_style())

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(self._table, stretch=1)

    def _wire_signals(self) -> None:
        self._create_button.clicked.connect(self.create_clicked.emit)
        self._refresh_button.clicked.connect(self.refresh_clicked.emit)

    def get_flight_number(self) -> str:
        return self._flight_input.text().strip().upper()

    def get_passenger_name(self) -> str:
        return self._passenger_input.text().strip()

    def set_flight_number(self, flight_number: str) -> None:
        self._flight_input.setText(flight_number or "")

    def clear_passenger(self) -> None:
        self._passenger_input.clear()

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()

    def set_status(self, message: str) -> None:
        self._status_label.setText(message)

    def set_loading(self, loading: bool) -> None:
        self._create_button.setDisabled(loading)
        self._refresh_button.setDisabled(loading)
        self._flight_input.setDisabled(loading)
        self._passenger_input.setDisabled(loading)
        self._create_button.setText("Creating…" if loading else "Create booking")

    def populate_table(self, bookings: list[Booking]) -> None:
        self._bookings = bookings
        self._table.setRowCount(len(bookings))

        for row, booking in enumerate(bookings):
            values = (
                booking.booking_id,
                booking.flight_number,
                booking.passenger_name,
                booking.status.value,
            )
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(6)

            confirm_btn = SuccessButton("Confirm")
            confirm_btn.setEnabled(booking.can_confirm)
            confirm_btn.clicked.connect(
                lambda checked=False, bid=booking.booking_id: self.confirm_clicked.emit(bid)
            )

            cancel_btn = DangerOutlineButton("Cancel")
            cancel_btn.setEnabled(booking.can_cancel)
            cancel_btn.clicked.connect(
                lambda checked=False, bid=booking.booking_id: self.cancel_clicked.emit(bid)
            )

            history_btn = SecondaryButton("History")
            history_btn.setMinimumWidth(76)
            history_btn.clicked.connect(
                lambda checked=False, bid=booking.booking_id: self.history_clicked.emit(bid)
            )

            actions_layout.addWidget(confirm_btn)
            actions_layout.addWidget(cancel_btn)
            actions_layout.addWidget(history_btn)
            actions_layout.addStretch()
            self._table.setCellWidget(row, 4, actions)

        if bookings:
            self.set_status(f"{len(bookings)} booking(s)")
        else:
            self.set_status("No bookings yet — create one above")
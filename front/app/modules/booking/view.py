from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Booking, BookingStatus


class BookingView(QWidget):
    create_clicked = Signal()
    confirm_clicked = Signal(str)
    cancel_clicked = Signal(str)
    refresh_clicked = Signal()

    _COLUMNS = ("ID", "Flight", "Passenger", "Status", "Actions")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bookings: list[Booking] = []
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("Bookings")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")

        subtitle = QLabel("Create a booking from a selected flight, then confirm or cancel")
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")

        form = QHBoxLayout()
        form.setSpacing(12)

        flight_box = QVBoxLayout()
        flight_box.setSpacing(4)
        flight_label = QLabel("Flight number")
        flight_label.setStyleSheet("color: #475569; font-size: 13px;")
        self._flight_input = QLineEdit()
        self._flight_input.setPlaceholderText("e.g. LY4257")
        self._flight_input.setStyleSheet(self._input_style())
        flight_box.addWidget(flight_label)
        flight_box.addWidget(self._flight_input)

        passenger_box = QVBoxLayout()
        passenger_box.setSpacing(4)
        passenger_label = QLabel("Passenger name")
        passenger_label.setStyleSheet("color: #475569; font-size: 13px;")
        self._passenger_input = QLineEdit()
        self._passenger_input.setPlaceholderText("Full name")
        self._passenger_input.setStyleSheet(self._input_style())
        passenger_box.addWidget(passenger_label)
        passenger_box.addWidget(self._passenger_input)

        self._create_button = QPushButton("Create booking")
        self._create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_button.setStyleSheet(self._primary_button_style())

        self._refresh_button = QPushButton("Refresh list")
        self._refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_button.setStyleSheet(self._secondary_button_style())

        form.addLayout(flight_box, stretch=1)
        form.addLayout(passenger_box, stretch=2)
        form.addWidget(self._create_button, alignment=Qt.AlignmentFlag.AlignBottom)
        form.addWidget(self._refresh_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #dc2626; font-size: 13px;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #64748b; font-size: 13px;")

        self._table = QTableWidget(0, len(self._COLUMNS))
        self._table.setHorizontalHeaderLabels(list(self._COLUMNS))
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setStyleSheet(
            """
            QTableWidget {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                font-size: 13px;
            }
            QHeaderView::section {
                background: #f8fafc;
                color: #475569;
                font-weight: 600;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            """
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(self._table, stretch=1)

    def _input_style(self) -> str:
        return """
            padding: 8px 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
            background: #ffffff;
        """

    def _primary_button_style(self) -> str:
        return """
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #93c5fd; }
        """

    def _secondary_button_style(self) -> str:
        return """
            QPushButton {
                background: #ffffff;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover { background: #f1f5f9; }
            QPushButton:disabled { color: #94a3b8; }
        """

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
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

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

            confirm_btn = QPushButton("Confirm")
            confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            confirm_btn.setStyleSheet(
                "QPushButton { background: #16a34a; color: white; border: none; "
                "border-radius: 6px; padding: 4px 10px; font-size: 12px; }"
                "QPushButton:disabled { background: #86efac; }"
            )
            confirm_btn.setEnabled(booking.status == BookingStatus.CREATED)
            confirm_btn.clicked.connect(
                lambda checked=False, bid=booking.booking_id: self.confirm_clicked.emit(bid)
            )

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setStyleSheet(
                "QPushButton { background: #ffffff; color: #dc2626; border: 1px solid #fecaca; "
                "border-radius: 6px; padding: 4px 10px; font-size: 12px; }"
                "QPushButton:disabled { color: #fca5a5; border-color: #fee2e2; }"
            )
            cancel_btn.setEnabled(booking.status != BookingStatus.CANCELLED)
            cancel_btn.clicked.connect(
                lambda checked=False, bid=booking.booking_id: self.cancel_clicked.emit(bid)
            )

            actions_layout.addWidget(confirm_btn)
            actions_layout.addWidget(cancel_btn)
            actions_layout.addStretch()
            self._table.setCellWidget(row, 4, actions)

        if bookings:
            self.set_status(f"{len(bookings)} booking(s)")
        else:
            self.set_status("No bookings yet — create one above")

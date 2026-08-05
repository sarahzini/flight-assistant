from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Flight
from app.shared.icon_cache import get_cached_pixmap
from app.shared.theme import (
    ErrorLabel,
    PrimaryButton,
    StatusLabel,
    field_label,
    input_style,
    page_subtitle,
    page_title,
    table_style,
)


class SearchView(QWidget):
    """The Search microfrontend: fully self-contained, with no knowledge of
    the Details microfrontend. Composing it next to a details panel is the
    shell's job (see ``app/shell/search_with_details.py``), not this View's.
    """

    search_clicked = Signal()
    row_selected = Signal(int)

    _COLUMNS = ("", "Flight", "Airline", "Route", "Status")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = page_title("Search Flights")
        subtitle = page_subtitle(
            "Search by departure airport — click a row; details appear on the right"
        )

        form_row = QHBoxLayout()
        form_row.setSpacing(12)

        dep_label = field_label("Departure IATA")

        self._dep_input = QLineEdit()
        self._dep_input.setPlaceholderText("TLV")
        self._dep_input.setMaxLength(3)
        self._dep_input.setFixedWidth(100)
        self._dep_input.setStyleSheet(input_style())

        limit_label = field_label("Limit")

        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, 20)
        self._limit_spin.setValue(5)
        self._limit_spin.setFixedWidth(80)
        self._limit_spin.setStyleSheet(input_style())

        self._search_button = PrimaryButton("Search")

        dep_box = QVBoxLayout()
        dep_box.setSpacing(4)
        dep_box.addWidget(dep_label)
        dep_box.addWidget(self._dep_input)

        limit_box = QVBoxLayout()
        limit_box.setSpacing(4)
        limit_box.addWidget(limit_label)
        limit_box.addWidget(self._limit_spin)

        form_row.addLayout(dep_box)
        form_row.addLayout(limit_box)
        form_row.addStretch()
        form_row.addWidget(self._search_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self._error_label = ErrorLabel()
        self._status_label = StatusLabel()

        self._table = QTableWidget(0, len(self._COLUMNS))
        self._table.setHorizontalHeaderLabels(list(self._COLUMNS))
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 36)
        self._table.setStyleSheet(table_style())

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form_row)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(self._table, stretch=1)

    def _wire_signals(self) -> None:
        self._search_button.clicked.connect(self.search_clicked.emit)
        self._dep_input.returnPressed.connect(self.search_clicked.emit)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            self.row_selected.emit(rows[0].row())
        else:
            self.row_selected.emit(-1)

    def get_dep_iata(self) -> str:
        return self._dep_input.text().strip().upper()

    def get_limit(self) -> int:
        return self._limit_spin.value()

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()

    def set_loading(self, loading: bool) -> None:
        self._search_button.setDisabled(loading)
        self._dep_input.setDisabled(loading)
        self._limit_spin.setDisabled(loading)
        self._search_button.setText("Searching…" if loading else "Search")

    def set_status(self, message: str) -> None:
        self._status_label.setText(message)

    def populate_table(self, flights: list[Flight]) -> None:
        """Pure rendering: fills the table from already-decided data. Deciding
        *what status message to show* is the Presenter's job, not the View's.
        """
        self._table.setRowCount(len(flights))
        for row, flight in enumerate(flights):
            route = f"{flight.departure.iata or '?'} → {flight.arrival.iata or '?'}"
            values = (
                "",
                flight.flight_number or "—",
                (flight.airline.name if flight.airline else None) or "—",
                route,
                flight.flight_status or "—",
            )
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

            if flight.airline and flight.airline.icon_url:
                pixmap = get_cached_pixmap(flight.airline.icon_url, size=24)
                if pixmap is not None:
                    icon_label = QLabel()
                    icon_label.setPixmap(pixmap)
                    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self._table.setCellWidget(row, 0, icon_label)

        if not flights:
            self._table.clearSelection()

    def clear_table(self) -> None:
        self._table.setRowCount(0)
        self._table.clearSelection()
        self.set_status("")
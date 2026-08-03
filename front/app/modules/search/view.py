from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Flight
from app.modules.details.view import FlightDetailsPanel
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
    search_clicked = Signal()
    row_selected = Signal(int)

    _COLUMNS = ("Flight", "Airline", "Route", "Status")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.details_panel = FlightDetailsPanel()
        self._sizes_initialized = False
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
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setStyleSheet(table_style())

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._table)
        self._splitter.addWidget(self.details_panel)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 0)
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)
        self._splitter.setHandleWidth(1)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form_row)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(self._splitter, stretch=1)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # The available width isn't known until the widget is actually shown,
        # so the table/details split is computed here instead of using a
        # hardcoded pixel width that would look wrong on other screen sizes.
        if not self._sizes_initialized and self.width() > 0:
            table_width = max(self.width() - FlightDetailsPanel.PANEL_WIDTH - 40, 200)
            self._splitter.setSizes([table_width, FlightDetailsPanel.PANEL_WIDTH])
            self._sizes_initialized = True

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
        self._table.setRowCount(len(flights))
        for row, flight in enumerate(flights):
            route = f"{flight.departure.iata or '?'} → {flight.arrival.iata or '?'}"
            values = (
                flight.flight_number or "—",
                (flight.airline.name if flight.airline else None) or "—",
                route,
                flight.flight_status or "—",
            )
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

        if flights:
            self.set_status(f"{len(flights)} flight(s) found — click a row for details on the right")
        else:
            self.set_status("No flights found for this airport")
            self._table.clearSelection()

    def clear_table(self) -> None:
        self._table.setRowCount(0)
        self._table.clearSelection()
        self.set_status("")

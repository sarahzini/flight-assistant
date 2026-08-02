from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import Flight
from app.modules.details.view import FlightDetailsPanel


class SearchView(QWidget):
    search_clicked = Signal()
    row_selected = Signal(int)

    _COLUMNS = ("Flight", "Airline", "Route", "Status")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.details_panel = FlightDetailsPanel()
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("Search Flights")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")

        subtitle = QLabel(
            "Search by departure airport — click a row; details appear on the right"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")

        form_row = QHBoxLayout()
        form_row.setSpacing(12)

        dep_label = QLabel("Departure IATA")
        dep_label.setStyleSheet("color: #475569; font-size: 13px;")

        self._dep_input = QLineEdit()
        self._dep_input.setPlaceholderText("TLV")
        self._dep_input.setMaxLength(3)
        self._dep_input.setFixedWidth(100)
        self._dep_input.setStyleSheet(self._input_style())

        limit_label = QLabel("Limit")
        limit_label.setStyleSheet("color: #475569; font-size: 13px;")

        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, 20)
        self._limit_spin.setValue(5)
        self._limit_spin.setFixedWidth(80)
        self._limit_spin.setStyleSheet(self._input_style())

        self._search_button = QPushButton("Search")
        self._search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_button.setStyleSheet(
            """
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #93c5fd; }
            """
        )

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

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #dc2626; font-size: 13px;")
        self._error_label.hide()

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #64748b; font-size: 13px;")

        self._table = QTableWidget(0, len(self._COLUMNS))
        self._table.setHorizontalHeaderLabels(list(self._COLUMNS))
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
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
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #0f172a;
            }
            """
        )

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._table)
        splitter.addWidget(self.details_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([720, FlightDetailsPanel.PANEL_WIDTH])
        splitter.setHandleWidth(1)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form_row)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(splitter, stretch=1)

    def _input_style(self) -> str:
        return """
            padding: 8px 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
            background: #ffffff;
        """

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
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

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

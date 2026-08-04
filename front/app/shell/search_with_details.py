"""Shell-level composition of the Search and Details microfrontends.

Strict microfrontend isolation means a module's View must never import
another module's View — composing independent microfrontends together is
the shell's responsibility. This container is the *only* place that knows
both ``SearchView`` and ``FlightDetailsPanel`` exist side by side; neither
of those Views is aware of the other.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from app.modules.details.view import FlightDetailsPanel
from app.modules.search.view import SearchView


class SearchWithDetailsContainer(QWidget):
    """Places the Search table and the Details side panel in one splitter."""

    def __init__(
        self,
        search_view: SearchView,
        details_panel: FlightDetailsPanel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._details_panel = details_panel
        self._sizes_initialized = False

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(search_view)
        self._splitter.addWidget(details_panel)
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
        # The available width isn't known until the widget is actually shown,
        # so the table/details split is computed here instead of using a
        # hardcoded pixel width that would look wrong on other screen sizes.
        if not self._sizes_initialized and self.width() > 0:
            table_width = max(self.width() - FlightDetailsPanel.PANEL_WIDTH - 40, 200)
            self._splitter.setSizes([table_width, FlightDetailsPanel.PANEL_WIDTH])
            self._sizes_initialized = True

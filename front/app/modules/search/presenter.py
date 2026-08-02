from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.api.client import ApiError
from app.modules.search.model import SearchModel
from app.modules.search.view import SearchView
from app.shared.app_state import AppState


class SearchPresenter(QObject):
    selection_changed = Signal()

    def __init__(self, view: SearchView, model: SearchModel, app_state: AppState) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._app_state = app_state

        view.search_clicked.connect(self._on_search)
        view.row_selected.connect(self._on_row_selected)

    def _on_search(self) -> None:
        dep_iata = self._view.get_dep_iata()

        if len(dep_iata) != 3 or not dep_iata.isalpha():
            self._view.set_error("Enter a valid 3-letter IATA code (e.g. TLV, JFK).")
            return

        limit = self._view.get_limit()
        self._view.clear_error()
        self._view.set_loading(True)

        try:
            flights = self._model.search(dep_iata, limit)
            self._app_state.set_search_results(flights)
            self._app_state.set_selected_flight(None)
            self._view.populate_table(flights)
            self.selection_changed.emit()
        except ApiError as exc:
            self._view.clear_table()
            self._app_state.set_search_results([])
            self._app_state.set_selected_flight(None)
            self._view.set_error(exc.message)
            self.selection_changed.emit()
        finally:
            self._view.set_loading(False)

    def _on_row_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._app_state.search_results):
            self._app_state.set_selected_flight(None)
        else:
            self._app_state.set_selected_flight(self._app_state.search_results[row])
        self.selection_changed.emit()

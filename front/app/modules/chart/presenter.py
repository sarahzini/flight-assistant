from __future__ import annotations

from PySide6.QtCore import QObject

from app.modules.chart import model as chart_model
from app.modules.chart.view import ChartView
from app.shared.app_state import AppState


class ChartPresenter(QObject):
    def __init__(self, view: ChartView, app_state: AppState) -> None:
        super().__init__()
        self._view = view
        self._app_state = app_state

    def refresh(self) -> None:
        flights = self._app_state.search_results
        if not flights:
            self._view.show_empty()
            return

        counts = chart_model.count_by_airline(flights)
        if chart_model.has_any_delay(flights):
            self._view.show_charts(
                count_by_airline=counts,
                secondary_title="Avg Departure Delay by Airline (min)",
                secondary_data=chart_model.avg_departure_delay_by_airline(flights),
                secondary_is_delay=True,
            )
        else:
            # AviationStack often returns null delays for scheduled flights —
            # show status breakdown instead of a useless all-zeros table.
            self._view.show_charts(
                count_by_airline=counts,
                secondary_title="Flights by Status",
                secondary_data={
                    k: float(v) for k, v in chart_model.count_by_status(flights).items()
                },
                secondary_is_delay=False,
            )

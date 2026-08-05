from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from app.api.client import ApiClient
from app.modules.advisor.model import AdvisorModel
from app.modules.advisor.presenter import AdvisorPresenter
from app.modules.advisor.view import AdvisorView
from app.modules.booking.model import BookingModel
from app.modules.booking.presenter import BookingPresenter
from app.modules.booking.view import BookingView
from app.modules.booking_history.model import BookingHistoryModel
from app.modules.booking_history.presenter import BookingHistoryPresenter
from app.modules.booking_history.view import BookingHistoryPanel
from app.modules.chart.presenter import ChartPresenter
from app.modules.chart.view import ChartView
from app.modules.details.model import DetailsModel
from app.modules.details.presenter import DetailsPresenter
from app.modules.details.view import FlightDetailsPanel
from app.modules.search.model import SearchModel
from app.modules.search.presenter import SearchPresenter
from app.modules.search.view import SearchView
from app.shared.app_state import AppState
from app.shared.session import Session
from app.shared.theme import Color
from app.shell.bookings_with_history import BookingsWithHistoryContainer
from app.shell.search_with_details import SearchWithDetailsContainer
from app.shell.sidebar import Sidebar

SEARCH_PAGE = 0
CHART_PAGE = 1
ADVISOR_PAGE = 2
BOOKINGS_PAGE = 3


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(
        self,
        session: Session,
        app_state: AppState,
        client: ApiClient,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._session = session
        self._app_state = app_state
        self._client = client

        self.setWindowTitle("Flight Assistant")
        self.setMinimumSize(960, 640)
        self.resize(1100, 720)

        central = QWidget()
        central.setObjectName("mainBackground")
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.set_user_email(session.email or "")

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentStack")

        self._stack.addWidget(self._build_search_page())
        self._stack.addWidget(self._build_chart_page())
        self._stack.addWidget(self._build_advisor_page())
        self._stack.addWidget(self._build_bookings_page())

        self._sidebar.page_selected.connect(self._on_page_selected)
        self._sidebar.logout_clicked.connect(self.logout_requested.emit)

        layout.addWidget(self._sidebar)
        layout.addWidget(self._stack, stretch=1)

        self.setCentralWidget(central)
        self._sidebar.set_current_page(SEARCH_PAGE)
        self._stack.setCurrentIndex(SEARCH_PAGE)

        self.setStyleSheet(
            f"""
            QWidget#mainBackground {{
                background: {Color.SLATE_100};
            }}
            QStackedWidget#contentStack {{
                background: {Color.SLATE_50};
            }}
            """
        )

    def _build_search_page(self) -> SearchWithDetailsContainer:
        # Search and Details are independent microfrontends — neither imports
        # the other. The shell is what composes them side by side.
        search_view = SearchView()
        details_panel = FlightDetailsPanel()

        search_model = SearchModel(self._client)
        self._search_presenter = SearchPresenter(search_view, search_model, self._app_state)

        details_model = DetailsModel(self._client)
        self._details_presenter = DetailsPresenter(details_panel, details_model, self._app_state)

        self._search_presenter.selection_changed.connect(self._details_presenter.refresh)
        self._search_presenter.selection_changed.connect(self._on_search_state_changed)
        return SearchWithDetailsContainer(search_view, details_panel)

    def _build_chart_page(self) -> ChartView:
        view = ChartView()
        self._chart_presenter = ChartPresenter(view, self._app_state)
        return view

    def _build_advisor_page(self) -> AdvisorView:
        view = AdvisorView()
        model = AdvisorModel(self._client)
        self._advisor_presenter = AdvisorPresenter(view, model)
        return view

    def _build_bookings_page(self) -> BookingsWithHistoryContainer:
        # Booking and Booking History are independent microfrontends — same
        # composition pattern as Search + Details above.
        view = BookingView()
        model = BookingModel(self._client)
        self._booking_presenter = BookingPresenter(
            view, model, self._session, self._app_state
        )
        self._booking_presenter.auth_expired.connect(self.logout_requested.emit)

        history_panel = BookingHistoryPanel()
        history_model = BookingHistoryModel(self._client)
        self._booking_history_presenter = BookingHistoryPresenter(history_panel, history_model)

        view.history_clicked.connect(self._booking_history_presenter.load)

        return BookingsWithHistoryContainer(view, history_panel)

    def _on_search_state_changed(self) -> None:
        if self._stack.currentIndex() == CHART_PAGE:
            self._chart_presenter.refresh()

    def _on_page_selected(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        if index == CHART_PAGE:
            self._chart_presenter.refresh()
        elif index == BOOKINGS_PAGE:
            self._booking_presenter.refresh()
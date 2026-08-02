"""Flight Assistant desktop application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from app.api.client import ApiClient
from app.shared.app_state import AppState
from app.shared.session import Session
from app.shell.login_window import LoginWindow
from app.shell.main_window import MainWindow


class FlightAssistantApp:
    def __init__(self) -> None:
        self._session = Session()
        self._app_state = AppState()
        self._client = ApiClient(session=self._session)
        self._login_window: LoginWindow | None = None
        self._main_window: MainWindow | None = None

    def start(self) -> int:
        app = QApplication(sys.argv)
        app.setApplicationName("Flight Assistant")
        app.aboutToQuit.connect(self._client.close)

        self._login_window = LoginWindow(self._session, self._client)
        self._login_window.login_succeeded.connect(self._on_login_succeeded)
        self._login_window.show()

        return app.exec()

    def _on_login_succeeded(self) -> None:
        if self._login_window is None:
            return

        self._login_window.hide()

        self._main_window = MainWindow(self._session, self._app_state, self._client)
        self._main_window.logout_requested.connect(self._on_logout)
        self._main_window.show()

    def _on_logout(self) -> None:
        self._session.clear()
        self._app_state.clear()

        if self._main_window is not None:
            self._main_window.close()
            self._main_window = None

        if self._login_window is not None:
            self._login_window.reset()
            self._login_window.show()


def main() -> int:
    return FlightAssistantApp().start()


if __name__ == "__main__":
    sys.exit(main())

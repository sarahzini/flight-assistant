from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from app.api.client import ApiClient, ApiError
from app.modules.login.model import LoginModel
from app.modules.login.presenter import LoginPresenter
from app.modules.login.view import LoginView
from app.shared.async_worker import AsyncTaskRunner
from app.shared.session import Session
from app.shared.theme import Color


class LoginWindow(QMainWindow, AsyncTaskRunner):
    login_succeeded = Signal()

    def __init__(self, session: Session, client: ApiClient, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._client = client

        self.setWindowTitle("Flight Assistant — Sign in")
        self.setMinimumSize(520, 560)
        self.resize(640, 680)

        container = QWidget()
        container.setObjectName("loginBackground")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)

        self._status_label = QLabel()
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        self._view = LoginView()
        layout.addWidget(self._view, stretch=1)

        model = LoginModel(client)
        self._presenter = LoginPresenter(self._view, model, session)
        self._presenter.login_succeeded.connect(self.login_succeeded.emit)

        self.setCentralWidget(container)
        self._apply_styles()
        self._check_backend()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#loginBackground {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eff6ff,
                    stop:0.5 #f8fafc,
                    stop:1 #eef2ff
                );
            }}
            QLabel#statusLabel {{
                font-size: 12px;
                color: {Color.SLATE_500};
                padding: 4px;
            }}
            """
        )

    def _check_backend(self) -> None:
        self._status_label.setText("Checking backend connection…")
        self._status_label.setStyleSheet(f"color: {Color.SLATE_500};")
        # Runs off the UI thread so a slow/unreachable backend never freezes
        # the login window on startup or after logging out.
        self.run_async(self._client.health_check, self._on_health_ok, self._on_health_failed)

    def _on_health_ok(self, health: dict) -> None:
        if health.get("status") == "ok":
            self._status_label.setText("Connected to backend")
            self._status_label.setStyleSheet(f"color: {Color.SUCCESS};")
        else:
            self._status_label.setText("Backend returned an unexpected response")
            self._status_label.setStyleSheet(f"color: {Color.WARNING};")

    def _on_health_failed(self, exc: Exception) -> None:
        message = exc.message if isinstance(exc, ApiError) else "Could not reach the backend."
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {Color.DANGER};")

    def reset(self) -> None:
        self._view.reset()
        self._check_backend()

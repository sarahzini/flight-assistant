from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QMainWindow, QVBoxLayout, QWidget

from app.api.client import ApiClient, ApiError
from app.modules.login.model import LoginModel
from app.modules.login.presenter import LoginPresenter
from app.modules.login.view import LoginView
from app.shared.session import Session


class LoginWindow(QMainWindow):
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
            """
            QWidget#loginBackground {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eff6ff,
                    stop:0.5 #f8fafc,
                    stop:1 #eef2ff
                );
            }
            QLabel#statusLabel {
                font-size: 12px;
                color: #64748b;
                padding: 4px;
            }
            """
        )

    def _check_backend(self) -> None:
        try:
            health = self._client.health_check()
            if health.get("status") == "ok":
                self._status_label.setText("Connected to backend")
                self._status_label.setStyleSheet("color: #16a34a;")
            else:
                self._status_label.setText("Backend returned an unexpected response")
                self._status_label.setStyleSheet("color: #ca8a04;")
        except ApiError as exc:
            self._status_label.setText(exc.message)
            self._status_label.setStyleSheet("color: #dc2626;")

    def reset(self) -> None:
        self._view.reset()
        self._check_backend()

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginView(QWidget):
    login_clicked = Signal()
    register_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 36, 32, 36)

        title = QLabel("Flight Assistant")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Sign in to manage flights and bookings")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Email address")
        self._email_input.setClearButtonEnabled(True)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self._error_label = QLabel()
        self._error_label.setObjectName("errorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.hide()

        self._login_button = QPushButton("Log in")
        self._login_button.setObjectName("primaryButton")
        self._login_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._register_button = QPushButton("Create account")
        self._register_button.setObjectName("secondaryButton")
        self._register_button.setCursor(Qt.CursorShape.PointingHandCursor)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._register_button)
        button_row.addWidget(self._login_button)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._email_input)
        card_layout.addWidget(self._password_input)
        card_layout.addWidget(self._error_label)
        card_layout.addSpacing(4)
        card_layout.addLayout(button_row)

        outer.addWidget(card)

        self.setStyleSheet(
            """
            QWidget#loginCard {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QLabel#loginTitle {
                font-size: 26px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#loginSubtitle {
                font-size: 13px;
                color: #64748b;
            }
            QLabel#errorLabel {
                color: #dc2626;
                font-size: 13px;
                padding: 4px 0;
            }
            QLineEdit {
                padding: 10px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                font-size: 14px;
                background: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #ffffff;
            }
            QPushButton#primaryButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover {
                background: #1d4ed8;
            }
            QPushButton#primaryButton:disabled {
                background: #93c5fd;
            }
            QPushButton#secondaryButton {
                background: transparent;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton#secondaryButton:hover {
                background: #f1f5f9;
            }
            QPushButton#secondaryButton:disabled {
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            """
        )

    def _wire_signals(self) -> None:
        self._login_button.clicked.connect(self.login_clicked.emit)
        self._register_button.clicked.connect(self.register_clicked.emit)
        self._password_input.returnPressed.connect(self.login_clicked.emit)

    def get_email(self) -> str:
        return self._email_input.text().strip()

    def get_password(self) -> str:
        return self._password_input.text()

    def set_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

    def set_loading(self, loading: bool) -> None:
        self._login_button.setDisabled(loading)
        self._register_button.setDisabled(loading)
        self._email_input.setDisabled(loading)
        self._password_input.setDisabled(loading)
        if loading:
            self._login_button.setText("Please wait…")
            self._register_button.setText("Please wait…")
        else:
            self._login_button.setText("Log in")
            self._register_button.setText("Create account")

    def reset(self) -> None:
        self._password_input.clear()
        self.clear_error()
        self.set_loading(False)

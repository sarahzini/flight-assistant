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

from app.shared.theme import Color, ErrorLabel, PrimaryButton, SecondaryButton


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

        icon = QLabel("✈")
        icon.setObjectName("loginIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        password_row = QHBoxLayout()
        password_row.setSpacing(0)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self._toggle_password_button = QPushButton("Show")
        self._toggle_password_button.setObjectName("togglePasswordButton")
        self._toggle_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_password_button.setCheckable(True)
        self._toggle_password_button.setFixedWidth(52)

        password_row.addWidget(self._password_input, stretch=1)
        password_row.addWidget(self._toggle_password_button)

        self._error_label = ErrorLabel()
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._login_button = PrimaryButton("Log in")
        self._register_button = SecondaryButton("Create account")

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._register_button)
        button_row.addWidget(self._login_button)

        card_layout.addWidget(icon)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._email_input)
        card_layout.addLayout(password_row)
        card_layout.addWidget(self._error_label)
        card_layout.addSpacing(4)
        card_layout.addLayout(button_row)

        outer.addWidget(card)

        self.setStyleSheet(
            f"""
            QWidget#loginCard {{
                background: {Color.WHITE};
                border-radius: 16px;
                border: 1px solid {Color.SLATE_200};
            }}
            QLabel#loginIcon {{
                font-size: 32px;
            }}
            QLabel#loginTitle {{
                font-size: 26px;
                font-weight: 700;
                color: {Color.INK};
            }}
            QLabel#loginSubtitle {{
                font-size: 13px;
                color: {Color.SLATE_500};
            }}
            QLineEdit {{
                padding: 10px 12px;
                border: 1px solid {Color.SLATE_300};
                border-radius: 8px;
                font-size: 14px;
                background: {Color.SLATE_50};
            }}
            QLineEdit:focus {{
                border-color: #3b82f6;
                background: {Color.WHITE};
            }}
            QLineEdit:disabled {{
                background: {Color.SLATE_100};
                color: {Color.SLATE_400};
            }}
            QPushButton#togglePasswordButton {{
                margin-left: 6px;
                padding: 10px 6px;
                border: 1px solid {Color.SLATE_300};
                border-radius: 8px;
                color: {Color.SLATE_600};
                font-size: 12px;
                background: {Color.SLATE_50};
            }}
            QPushButton#togglePasswordButton:hover {{
                background: {Color.SLATE_100};
            }}
            QPushButton#togglePasswordButton:checked {{
                background: {Color.PRIMARY_SOFT};
                border-color: {Color.PRIMARY_SOFT_BORDER};
                color: {Color.PRIMARY};
            }}
            """
        )

    def _wire_signals(self) -> None:
        self._login_button.clicked.connect(self.login_clicked.emit)
        self._register_button.clicked.connect(self.register_clicked.emit)
        self._email_input.returnPressed.connect(self.login_clicked.emit)
        self._password_input.returnPressed.connect(self.login_clicked.emit)
        self._toggle_password_button.toggled.connect(self._on_toggle_password)

    def _on_toggle_password(self, checked: bool) -> None:
        self._password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self._toggle_password_button.setText("Hide" if checked else "Show")

    def get_email(self) -> str:
        return self._email_input.text().strip()

    def get_password(self) -> str:
        return self._password_input.text()

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()

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
        self._toggle_password_button.setChecked(False)
        self.clear_error()
        self.set_loading(False)

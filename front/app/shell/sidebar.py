from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.shared.theme import Color

NAV_ITEMS = (
    ("Search", "🔍", "Search for flights by departure airport"),
    ("Chart", "📊", "Charts for your latest search results"),
    ("Advisor", "💬", "Ask the AI advisor aviation questions"),
    ("Bookings", "🎫", "Create and manage your bookings"),
)


class Sidebar(QFrame):
    page_selected = Signal(int)
    logout_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)

        brand_row = QLabel("✈  Flight Assistant")
        brand_row.setObjectName("sidebarTitle")
        brand_row.setWordWrap(True)

        self._email_label = QLabel()
        self._email_label.setObjectName("sidebarEmail")
        self._email_label.setWordWrap(True)

        layout.addWidget(brand_row)
        layout.addWidget(self._email_label)
        layout.addSpacing(20)

        self._nav_buttons: list[QPushButton] = []
        for index, (name, icon, tooltip) in enumerate(NAV_ITEMS):
            button = QPushButton(f"{icon}   {name}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(tooltip)
            button.clicked.connect(lambda checked, i=index: self._on_nav_clicked(i))
            layout.addWidget(button)
            self._nav_buttons.append(button)

        layout.addStretch()

        self._logout_button = QPushButton("⎋  Log out")
        self._logout_button.setObjectName("logoutButton")
        self._logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._logout_button.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(self._logout_button)

        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame#sidebar {{
                background: {Color.SIDEBAR_BG};
                border-right: 1px solid {Color.SIDEBAR_BORDER};
            }}
            QLabel#sidebarTitle {{
                color: {Color.SIDEBAR_TEXT_BRIGHT};
                font-size: 17px;
                font-weight: 700;
            }}
            QLabel#sidebarEmail {{
                color: {Color.SIDEBAR_TEXT_MUTED};
                font-size: 12px;
            }}
            QPushButton#navButton {{
                text-align: left;
                padding: 10px 14px;
                border: none;
                border-radius: 8px;
                color: {Color.SIDEBAR_TEXT};
                font-size: 14px;
                background: transparent;
            }}
            QPushButton#navButton:hover {{
                background: {Color.SIDEBAR_HOVER};
                color: {Color.SIDEBAR_TEXT_BRIGHT};
            }}
            QPushButton#navButton:checked {{
                background: {Color.PRIMARY};
                color: {Color.WHITE};
                font-weight: 600;
            }}
            QPushButton#navButton:disabled {{
                color: #475569;
            }}
            QPushButton#logoutButton {{
                text-align: left;
                padding: 10px 14px;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #fca5a5;
                background: transparent;
                font-size: 13px;
            }}
            QPushButton#logoutButton:hover {{
                background: {Color.SIDEBAR_HOVER};
                border-color: #475569;
            }}
            """
        )

    def set_user_email(self, email: str) -> None:
        self._email_label.setText(email)

    def set_current_page(self, index: int) -> None:
        for i, button in enumerate(self._nav_buttons):
            button.setChecked(i == index)

    def set_nav_enabled(self, index: int, enabled: bool) -> None:
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setEnabled(enabled)

    def _on_nav_clicked(self, index: int) -> None:
        self.set_current_page(index)
        self.page_selected.emit(index)

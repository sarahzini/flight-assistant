"""Central design system for the Flight Assistant desktop UI.

Colors, spacing, typography, and small reusable styled widgets live here
instead of being redefined (slightly differently, every time) in every
module's view. This keeps every screen visually consistent and makes the
whole app restylable from a single place.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QWidget


class Color:
    """Brand, feedback, and neutral palette shared by every screen."""

    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    PRIMARY_DISABLED = "#93c5fd"
    PRIMARY_SOFT = "#eff6ff"
    PRIMARY_SOFT_BORDER = "#bfdbfe"
    ACCENT = "#0891b2"
    ACCENT_ALT = "#0d9488"

    DANGER = "#dc2626"
    DANGER_SOFT = "#fef2f2"
    DANGER_SOFT_BORDER = "#fecaca"
    SUCCESS = "#16a34a"
    SUCCESS_HOVER = "#15803d"
    SUCCESS_SOFT = "#86efac"
    WARNING = "#ca8a04"

    INK = "#0f172a"
    SLATE_700 = "#334155"
    SLATE_600 = "#475569"
    SLATE_500 = "#64748b"
    SLATE_400 = "#94a3b8"
    SLATE_300 = "#cbd5e1"
    SLATE_200 = "#e2e8f0"
    SLATE_100 = "#f1f5f9"
    SLATE_50 = "#f8fafc"
    WHITE = "#ffffff"

    SIDEBAR_BG = "#0f172a"
    SIDEBAR_BORDER = "#1e293b"
    SIDEBAR_HOVER = "#1e293b"
    SIDEBAR_TEXT = "#cbd5e1"
    SIDEBAR_TEXT_MUTED = "#94a3b8"
    SIDEBAR_TEXT_BRIGHT = "#f1f5f9"


class Space:
    """4px-based spacing scale used across layouts and margins."""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32


class Font:
    TITLE = 22
    HEADING = 18
    SUBHEADING = 14
    BODY = 14
    SMALL = 13
    TINY = 11


PAGE_MARGINS = (Space.XXL, Space.XL + 4, Space.XXL, Space.XL + 4)
PAGE_SPACING = Space.LG


# --- Shared QSS fragments -----------------------------------------------


def page_title_style() -> str:
    return f"font-size: {Font.TITLE}px; font-weight: 700; color: {Color.INK};"


def page_subtitle_style() -> str:
    return f"font-size: {Font.SMALL}px; color: {Color.SLATE_500};"


def field_label_style() -> str:
    return f"color: {Color.SLATE_600}; font-size: {Font.SMALL}px; font-weight: 500;"


def section_heading_style() -> str:
    return f"font-size: {Font.SMALL}px; color: {Color.SLATE_600}; font-weight: 600;"


def input_style() -> str:
    return f"""
        QLineEdit, QSpinBox, QTextEdit {{
            padding: 9px 12px;
            border: 1px solid {Color.SLATE_300};
            border-radius: 8px;
            font-size: {Font.BODY}px;
            background: {Color.WHITE};
            color: {Color.INK};
            selection-background-color: {Color.PRIMARY_SOFT_BORDER};
        }}
        QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {{
            border: 1px solid {Color.PRIMARY};
            background: {Color.WHITE};
        }}
        QLineEdit:disabled, QSpinBox:disabled, QTextEdit:disabled {{
            background: {Color.SLATE_100};
            color: {Color.SLATE_400};
        }}
    """


def table_style() -> str:
    return f"""
        QTableWidget {{
            background: {Color.WHITE};
            border: 1px solid {Color.SLATE_200};
            border-radius: 10px;
            gridline-color: {Color.SLATE_100};
            font-size: {Font.SMALL}px;
        }}
        QHeaderView::section {{
            background: {Color.SLATE_50};
            color: {Color.SLATE_600};
            font-weight: 600;
            padding: 10px 8px;
            border: none;
            border-bottom: 1px solid {Color.SLATE_200};
        }}
        QTableWidget::item {{
            padding: 4px 2px;
        }}
        QTableWidget::item:selected {{
            background: #dbeafe;
            color: {Color.INK};
        }}
    """


def card_style(object_name: Optional[str] = None) -> str:
    selector = f"QFrame#{object_name}" if object_name else "QFrame"
    return f"""
        {selector} {{
            background: {Color.WHITE};
            border: 1px solid {Color.SLATE_200};
            border-radius: 10px;
        }}
    """


# --- Reusable styled widgets ---------------------------------------------


class PrimaryButton(QPushButton):
    """The main call-to-action button (blue fill)."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {Color.PRIMARY};
                color: {Color.WHITE};
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                font-size: {Font.SMALL}px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {Color.PRIMARY_HOVER}; }}
            QPushButton:disabled {{ background: {Color.PRIMARY_DISABLED}; }}
            """
        )


class SecondaryButton(QPushButton):
    """A lower-emphasis outlined button, used next to a PrimaryButton."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {Color.WHITE};
                color: {Color.SLATE_600};
                border: 1px solid {Color.SLATE_300};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: {Font.SMALL}px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {Color.SLATE_100}; }}
            QPushButton:disabled {{ color: {Color.SLATE_400}; border-color: {Color.SLATE_200}; }}
            """
        )


class GhostIconButton(QPushButton):
    """A small square icon-only button (e.g. the details "refresh" button)."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {Color.PRIMARY_SOFT};
                color: {Color.PRIMARY};
                border: 1px solid {Color.PRIMARY_SOFT_BORDER};
                border-radius: 7px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {Color.PRIMARY_SOFT_BORDER}; }}
            QPushButton:disabled {{ color: {Color.PRIMARY_DISABLED}; }}
            """
        )


class SuccessButton(QPushButton):
    """A small filled green button, used for row-level confirm actions."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Without a minimum width, a table cell widget can squeeze this
        # button below its natural size and clip the label text.
        self.setMinimumWidth(76)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {Color.SUCCESS};
                color: {Color.WHITE};
                border: none;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: {Font.TINY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {Color.SUCCESS_HOVER}; }}
            QPushButton:disabled {{ background: {Color.SUCCESS_SOFT}; }}
            """
        )


class DangerOutlineButton(QPushButton):
    """A small outlined red button, used for row-level destructive actions."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Without a minimum width, a table cell widget can squeeze this
        # button below its natural size and clip the label text.
        self.setMinimumWidth(76)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {Color.WHITE};
                color: {Color.DANGER};
                border: 1px solid {Color.DANGER_SOFT_BORDER};
                border-radius: 6px;
                padding: 5px 12px;
                font-size: {Font.TINY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {Color.DANGER_SOFT}; }}
            QPushButton:disabled {{ color: #fca5a5; border-color: #fee2e2; }}
            """
        )


class ErrorLabel(QLabel):
    """A red, word-wrapped label that hides itself when there is no error."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        self.setStyleSheet(f"color: {Color.DANGER}; font-size: {Font.SMALL}px;")
        self.hide()

    def set_message(self, message: str) -> None:
        self.setText(message)
        self.show()

    def clear_message(self) -> None:
        self.clear()
        self.hide()


class StatusLabel(QLabel):
    """A muted, word-wrapped label for non-error status/help text."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        self.setStyleSheet(f"color: {Color.SLATE_500}; font-size: {Font.SMALL}px;")


class Card(QFrame):
    """A white, rounded, bordered container used to group related fields."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background: {Color.SLATE_50}; border: 1px solid {Color.SLATE_200}; "
            "border-radius: 8px; }}"
        )


def page_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(page_title_style())
    return label


def page_subtitle(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(page_subtitle_style())
    return label


def field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(field_label_style())
    return label

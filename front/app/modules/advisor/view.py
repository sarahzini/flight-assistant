from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import AdvisorAnswer
from app.shared.theme import (
    Color,
    ErrorLabel,
    PrimaryButton,
    StatusLabel,
    field_label,
    input_style,
    page_subtitle,
    page_title,
    section_heading_style,
)


class AdvisorView(QWidget):
    ask_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = page_title("AI Advisor")
        subtitle = page_subtitle(
            "Ask aviation questions — answered from the knowledge base (RAG). "
            "Try: “What is a connection?” or “Baggage rules?”"
        )

        question_label = field_label("Your question")

        self._question_input = QTextEdit()
        self._question_input.setPlaceholderText("Type your question here…")
        self._question_input.setFixedHeight(100)
        self._question_input.setStyleSheet(input_style())

        button_row = QHBoxLayout()
        self._ask_button = PrimaryButton("Ask")
        button_row.addWidget(self._ask_button)
        button_row.addStretch()

        self._error_label = ErrorLabel()
        self._status_label = StatusLabel()

        answer_label = QLabel("Answer")
        answer_label.setStyleSheet(section_heading_style())

        self._answer_output = QTextEdit()
        self._answer_output.setReadOnly(True)
        self._answer_output.setPlaceholderText("The answer will appear here…")
        self._answer_output.setStyleSheet(
            f"""
            QTextEdit {{
                padding: 12px;
                border: 1px solid {Color.SLATE_200};
                border-radius: 8px;
                font-size: 14px;
                background: {Color.WHITE};
                color: {Color.INK};
            }}
            """
        )

        sources_label = QLabel("Sources")
        sources_label.setStyleSheet(section_heading_style())

        self._sources_list = QListWidget()
        self._sources_list.setMaximumHeight(120)
        self._sources_list.setStyleSheet(
            f"""
            QListWidget {{
                background: {Color.SLATE_50};
                border: 1px solid {Color.SLATE_200};
                border-radius: 8px;
                font-size: 13px;
                padding: 4px;
            }}
            """
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(question_label)
        layout.addWidget(self._question_input)
        layout.addLayout(button_row)
        layout.addWidget(self._error_label)
        layout.addWidget(self._status_label)
        layout.addWidget(answer_label)
        layout.addWidget(self._answer_output, stretch=1)
        layout.addWidget(sources_label)
        layout.addWidget(self._sources_list)

    def _wire_signals(self) -> None:
        self._ask_button.clicked.connect(self.ask_clicked.emit)

    def get_question(self) -> str:
        return self._question_input.toPlainText().strip()

    def set_error(self, message: str) -> None:
        self._error_label.set_message(message)

    def clear_error(self) -> None:
        self._error_label.clear_message()

    def set_loading(self, loading: bool) -> None:
        self._ask_button.setDisabled(loading)
        self._question_input.setDisabled(loading)
        self._ask_button.setText("Thinking…" if loading else "Ask")
        if loading:
            self._status_label.setText("Asking the advisor (this may take up to a minute)…")
        else:
            self._status_label.clear()

    def show_answer(self, answer: AdvisorAnswer) -> None:
        self._answer_output.setPlainText(answer.answer)
        self._sources_list.clear()
        for source in answer.sources:
            self._sources_list.addItem(source)
        if answer.sources:
            self._status_label.setText(f"Answer ready — {len(answer.sources)} source(s)")
        else:
            self._status_label.setText("Answer ready")

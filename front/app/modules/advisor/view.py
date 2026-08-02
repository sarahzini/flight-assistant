from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import AdvisorAnswer


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

        title = QLabel("AI Advisor")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")

        subtitle = QLabel(
            "Ask aviation questions — answered from the knowledge base (RAG). "
            "Try: “What is a connection?” or “Baggage rules?”"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")

        question_label = QLabel("Your question")
        question_label.setStyleSheet("color: #475569; font-size: 13px;")

        self._question_input = QTextEdit()
        self._question_input.setPlaceholderText("Type your question here…")
        self._question_input.setFixedHeight(100)
        self._question_input.setStyleSheet(
            """
            QTextEdit {
                padding: 10px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                font-size: 14px;
                background: #ffffff;
            }
            """
        )

        button_row = QHBoxLayout()
        self._ask_button = QPushButton("Ask")
        self._ask_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ask_button.setStyleSheet(
            """
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 28px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #93c5fd; }
            """
        )
        button_row.addWidget(self._ask_button)
        button_row.addStretch()

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #dc2626; font-size: 13px;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #64748b; font-size: 13px;")

        answer_label = QLabel("Answer")
        answer_label.setStyleSheet("color: #475569; font-size: 13px; font-weight: 600;")

        self._answer_output = QTextEdit()
        self._answer_output.setReadOnly(True)
        self._answer_output.setPlaceholderText("The answer will appear here…")
        self._answer_output.setStyleSheet(
            """
            QTextEdit {
                padding: 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background: #ffffff;
                color: #0f172a;
            }
            """
        )

        sources_label = QLabel("Sources")
        sources_label.setStyleSheet("color: #475569; font-size: 13px; font-weight: 600;")

        self._sources_list = QListWidget()
        self._sources_list.setMaximumHeight(120)
        self._sources_list.setStyleSheet(
            """
            QListWidget {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
                padding: 4px;
            }
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
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

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

from __future__ import annotations

from PySide6.QtCore import QObject

from app.api.client import error_message
from app.domain.models import AdvisorAnswer
from app.modules.advisor.model import AdvisorModel
from app.modules.advisor.view import AdvisorView
from app.shared.async_worker import AsyncTaskRunner


class AdvisorPresenter(QObject, AsyncTaskRunner):
    def __init__(self, view: AdvisorView, model: AdvisorModel) -> None:
        super().__init__()
        self._view = view
        self._model = model

        view.ask_clicked.connect(self._on_ask)

    def _on_ask(self) -> None:
        question = self._view.get_question()
        if not question:
            self._view.set_error("Please enter a question.")
            return

        self._view.clear_error()
        self._view.set_loading(True)

        self.run_async(lambda: self._model.ask(question), self._on_ask_success, self._on_ask_error)

    def _on_ask_success(self, answer: AdvisorAnswer) -> None:
        self._view.set_loading(False)
        self._view.show_answer(answer)

    def _on_ask_error(self, exc: Exception) -> None:
        self._view.set_loading(False)
        self._view.set_error(error_message(exc))

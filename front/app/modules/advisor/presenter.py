from __future__ import annotations

from PySide6.QtCore import QObject

from app.api.client import ApiError
from app.modules.advisor.model import AdvisorModel
from app.modules.advisor.view import AdvisorView


class AdvisorPresenter(QObject):
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

        try:
            answer = self._model.ask(question)
            self._view.show_answer(answer)
        except ApiError as exc:
            self._view.set_error(exc.message)
        finally:
            self._view.set_loading(False)

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.api.client import ApiError
from app.modules.login.model import LoginModel
from app.modules.login.view import LoginView
from app.shared.session import Session


class LoginPresenter(QObject):
    login_succeeded = Signal()

    def __init__(self, view: LoginView, model: LoginModel, session: Session) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._session = session

        view.login_clicked.connect(self._on_login)
        view.register_clicked.connect(self._on_register)

    def _validate(self) -> bool:
        email = self._view.get_email()
        password = self._view.get_password()

        if not email or not password:
            self._view.set_error("Please enter your email and password.")
            return False
        if "@" not in email:
            self._view.set_error("Please enter a valid email address.")
            return False
        if len(password) < 4:
            self._view.set_error("Password must be at least 4 characters.")
            return False
        return True

    def _on_login(self) -> None:
        if not self._validate():
            return

        email = self._view.get_email()
        password = self._view.get_password()
        self._view.clear_error()
        self._view.set_loading(True)

        try:
            token = self._model.login(email, password)
            self._session.set_auth(token.access_token, email)
            self.login_succeeded.emit()
        except ApiError as exc:
            self._view.set_error(exc.message)
        finally:
            self._view.set_loading(False)

    def _on_register(self) -> None:
        if not self._validate():
            return

        email = self._view.get_email()
        password = self._view.get_password()
        self._view.clear_error()
        self._view.set_loading(True)

        try:
            self._model.register(email, password)
            token = self._model.login(email, password)
            self._session.set_auth(token.access_token, email)
            self.login_succeeded.emit()
        except ApiError as exc:
            self._view.set_error(exc.message)
        finally:
            self._view.set_loading(False)

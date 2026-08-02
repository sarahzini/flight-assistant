from __future__ import annotations

from app.api import auth as auth_api
from app.api.client import ApiClient
from app.domain.models import Token, UserOut


class LoginModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def register(self, email: str, password: str) -> UserOut:
        return auth_api.register(self._client, email, password)

    def login(self, email: str, password: str) -> Token:
        return auth_api.login(self._client, email, password)

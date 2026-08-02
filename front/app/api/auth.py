from __future__ import annotations

from app.api.client import ApiClient
from app.domain.models import Token, UserOut


def register(client: ApiClient, email: str, password: str) -> UserOut:
    data = client.post("/auth/register", json={"email": email, "password": password})
    return UserOut.from_dict(data)


def login(client: ApiClient, email: str, password: str) -> Token:
    data = client.post("/auth/login", json={"email": email, "password": password})
    return Token.from_dict(data)

from __future__ import annotations

from typing import Optional


class Session:
    """In-memory JWT session for the authenticated user."""

    def __init__(self) -> None:
        self.token: Optional[str] = None
        self.email: Optional[str] = None

    def is_authenticated(self) -> bool:
        return self.token is not None

    def set_auth(self, token: str, email: str) -> None:
        self.token = token
        self.email = email

    def clear(self) -> None:
        self.token = None
        self.email = None

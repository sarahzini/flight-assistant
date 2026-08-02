from __future__ import annotations

from app.api import advisor as advisor_api
from app.api.client import ApiClient
from app.domain.models import AdvisorAnswer


class AdvisorModel:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def ask(self, question: str) -> AdvisorAnswer:
        return advisor_api.ask(self._client, question)

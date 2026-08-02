from __future__ import annotations

from app.api.client import ApiClient
from app.domain.models import AdvisorAnswer


def ask(client: ApiClient, question: str) -> AdvisorAnswer:
    data = client.post("/advisor", json={"question": question})
    return AdvisorAnswer.from_dict(data)

from __future__ import annotations

from typing import Any, Optional

import httpx

from app.config import BASE_URL
from app.shared.session import Session


class ApiError(Exception):
    """User-facing API error with a message suitable for the UI."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def map_http_error(exc: httpx.HTTPStatusError) -> ApiError:
    status = exc.response.status_code
    detail = _extract_detail(exc.response)

    messages = {
        401: detail or "Please log in",
        403: "You do not have permission to perform this action",
        404: "Not found",
        400: detail or "Invalid request",
        422: detail or "Invalid request",
        500: "Server error — please try again later",
    }
    message = messages.get(status, detail or f"Request failed ({status})")
    return ApiError(message, status_code=status)


def _extract_detail(response: httpx.Response) -> Optional[str]:
    try:
        payload = response.json()
    except ValueError:
        return None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and detail:
            first = detail[0]
            if isinstance(first, dict):
                return first.get("msg")
    return None


class ApiClient:
    """Shared HTTP client for the FastAPI backend."""

    def __init__(self, session: Optional[Session] = None, base_url: str = BASE_URL) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self._base_url, timeout=60.0)

    def close(self) -> None:
        self._client.close()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._session and self._session.token:
            headers["Authorization"] = f"Bearer {self._session.token}"
        return headers

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        try:
            response = self._client.get(path, params=params, headers=self._headers())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise map_http_error(exc) from exc
        except httpx.RequestError as exc:
            raise ApiError("Could not reach the server — is the backend running?") from exc

    def post(self, path: str, json: Optional[dict[str, Any]] = None) -> Any:
        try:
            response = self._client.post(path, json=json, headers=self._headers())
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise map_http_error(exc) from exc
        except httpx.RequestError as exc:
            raise ApiError("Could not reach the server — is the backend running?") from exc

    def health_check(self) -> dict[str, str]:
        return self.get("/health")

"""Caches remote icon pixmaps by URL so the same image is only downloaded once,
even if many table rows reference it (e.g. the generic airplane icon)."""

from __future__ import annotations

from PySide6.QtGui import QPixmap

from app.shared.remote_image import load_remote_pixmap

_cache: dict[str, QPixmap | None] = {}


def get_cached_pixmap(url: str, size: int = 24) -> QPixmap | None:
    key = f"{url}:{size}"
    if key not in _cache:
        _cache[key] = load_remote_pixmap(url, size)
    return _cache[key]
"""Small helper to load an image from a URL into a QLabel.

Qt has no built-in way to display a remote image directly — the bytes must
be fetched first, then turned into a QPixmap. This keeps that logic in one
place instead of repeating it in every module that wants a remote icon.
"""

from __future__ import annotations

import httpx
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


def load_remote_pixmap(url: str, size: int) -> QPixmap | None:
    """Download an image and return it as a square QPixmap, or None on failure.

    Runs synchronously — only intended for small, one-off icons (like a
    header avatar) fetched once when a screen is built, not for large lists.
    """
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    pixmap = QPixmap()
    if not pixmap.loadFromData(response.content):
        return None

    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def make_remote_icon_label(url: str, size: int = 40) -> QLabel:
    """Build a QLabel showing a remote image, or an empty label if it fails to load."""
    label = QLabel()
    label.setFixedSize(size, size)
    pixmap = load_remote_pixmap(url, size)
    if pixmap is not None:
        label.setPixmap(pixmap)
    return label
"""Run blocking API calls off the Qt UI thread.

Every HTTP call in this app goes through ``httpx`` synchronously. Without this
helper, a slow call (e.g. the AI Advisor, which can take up to a minute) would
freeze the entire window — no repainting, no button feedback, and Windows may
even flag the app as "Not Responding". Presenters that talk to the API mix in
:class:`AsyncTaskRunner` and call :meth:`run_async` instead of calling the
model directly on the UI thread.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from PySide6.QtCore import QThread, Signal

# Every live worker is tracked here so the app can wait for them on shutdown.
# Without this, quitting while a call is still in flight (e.g. closing the
# app mid-Advisor-request) would let Qt try to destroy a QThread whose run()
# hasn't returned yet — which is a fatal, unrecoverable crash in Qt/PySide.
_active_workers: set["AsyncWorker"] = set()


class AsyncWorker(QThread):
    """Runs ``fn`` on a background thread and reports the outcome via signals."""

    succeeded = Signal(object)
    failed = Signal(object)

    def __init__(self, fn: Callable[[], Any], parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._fn = fn
        _active_workers.add(self)
        self.finished.connect(lambda: _active_workers.discard(self))

    def run(self) -> None:
        try:
            result = self._fn()
        except Exception as exc:  # noqa: BLE001 - forwarded to the caller's error handler
            self.failed.emit(exc)
        else:
            self.succeeded.emit(result)


def shutdown_workers(timeout_ms: int = 5000) -> None:
    """Wait for any in-flight background calls to finish before the app exits.

    Connect this to ``QApplication.aboutToQuit``. It must run before Qt starts
    tearing down windows/presenters, otherwise a still-running worker thread
    could be destroyed mid-flight and crash the process.
    """
    for worker in list(_active_workers):
        if worker.isRunning():
            worker.quit()
            if not worker.wait(timeout_ms):
                worker.terminate()
                worker.wait()


class AsyncTaskRunner:
    """Mixin for QObject-based presenters/windows that need to call the API
    without blocking the UI thread.

    ``on_success``/``on_error`` are always delivered on the thread the
    presenter itself lives in (the Qt main thread), because they are invoked
    from real bound methods of ``self`` — Qt detects the cross-thread signal
    emission from :class:`AsyncWorker` and automatically queues the call, so
    it is always safe to touch widgets from these callbacks.
    """

    _active_worker: Optional[AsyncWorker] = None
    _pending_success: Optional[Callable[[Any], None]] = None
    _pending_error: Optional[Callable[[Exception], None]] = None

    def run_async(
        self,
        fn: Callable[[], Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        self._pending_success = on_success
        self._pending_error = on_error

        worker = AsyncWorker(fn, parent=self)
        self._active_worker = worker
        worker.succeeded.connect(self._on_worker_succeeded)
        worker.failed.connect(self._on_worker_failed)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _on_worker_succeeded(self, result: Any) -> None:
        handler, self._pending_success = self._pending_success, None
        if handler is not None:
            handler(result)

    def _on_worker_failed(self, exc: Exception) -> None:
        handler, self._pending_error = self._pending_error, None
        if handler is not None:
            handler(exc)

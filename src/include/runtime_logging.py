"""Central runtime error logging for the FcsIT desktop application."""

import atexit
import faulthandler
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path


_LOCK = threading.RLock()
_LOG_HANDLE = None
_ORIGINAL_STDERR = None
_TEE_STREAM = None


class _TeeStream:
    """Mirror standard error to the terminal and the runtime log."""

    def __init__(self, terminal, log_handle):
        self.terminal = terminal
        self.log_handle = log_handle

    def write(self, message):
        with _LOCK:
            if self.terminal is not None:
                self.terminal.write(message)
            self.log_handle.write(message)
        return len(message)

    def flush(self):
        with _LOCK:
            if self.terminal is not None:
                self.terminal.flush()
            self.log_handle.flush()

    def isatty(self):
        return bool(self.terminal and self.terminal.isatty())

    @property
    def encoding(self):
        return getattr(self.terminal, 'encoding', 'utf-8')


def configure_runtime_logging(base_directory):
    """Create ``runtime_log.txt`` and mirror Python errors into it."""
    global _LOG_HANDLE, _ORIGINAL_STDERR, _TEE_STREAM
    if _LOG_HANDLE is not None:
        return Path(_LOG_HANDLE.name)

    log_path = Path(base_directory).resolve() / 'runtime_log.txt'
    _LOG_HANDLE = log_path.open('a', encoding='utf-8', buffering=1)
    _ORIGINAL_STDERR = sys.stderr
    _TEE_STREAM = _TeeStream(_ORIGINAL_STDERR, _LOG_HANDLE)
    sys.stderr = _TEE_STREAM
    _LOG_HANDLE.write(
        f"\n{'=' * 78}\nFcsIT session started: {datetime.now().isoformat()}\n"
    )
    _LOG_HANDLE.flush()
    faulthandler.enable(file=_LOG_HANDLE, all_threads=True)
    return log_path


def log_exception(context, exception):
    """Write a caught exception and its active traceback to the runtime log."""
    with _LOCK:
        target = _LOG_HANDLE if _LOG_HANDLE is not None else sys.stderr
        target.write(
            f"\n[{datetime.now().isoformat()}] {context}\n"
        )
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=target
        )
        target.flush()


def _close_runtime_logging():
    global _LOG_HANDLE
    if _LOG_HANDLE is None:
        return
    try:
        faulthandler.disable()
        sys.stderr = _ORIGINAL_STDERR
        _LOG_HANDLE.write(
            f"FcsIT session ended: {datetime.now().isoformat()}\n"
        )
        _LOG_HANDLE.flush()
        _LOG_HANDLE.close()
    finally:
        _LOG_HANDLE = None


atexit.register(_close_runtime_logging)

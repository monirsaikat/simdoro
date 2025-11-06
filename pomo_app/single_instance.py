import socket
from typing import Optional


class SingleInstanceLock:
    """Ensures only a single application instance is running."""

    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None

    def acquire(self) -> None:
        if self._socket:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise RuntimeError("Another instance is already running.") from exc
        self._socket = sock

    def release(self) -> None:
        if self._socket:
            self._socket.close()
            self._socket = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

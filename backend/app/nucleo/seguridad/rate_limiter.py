from collections import deque
from threading import Lock
from time import monotonic


class AuthRateLimiter:
    """Límite por proceso para el despliegue local de un único worker."""

    def __init__(self):
        self.attempts: dict[str, deque] = {}
        self.lock = Lock()

    def allow(self, client: str) -> bool:
        now = monotonic()
        with self.lock:
            if len(self.attempts) >= 4096:
                self.attempts = {k: v for k, v in self.attempts.items() if v and v[-1] > now - 60}
                if client not in self.attempts and len(self.attempts) >= 4096:
                    return False
            recent = self.attempts.setdefault(client, deque())
            while recent and recent[0] <= now - 60:
                recent.popleft()
            if len(recent) >= 30:
                return False
            recent.append(now)
            return True

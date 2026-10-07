from collections import deque
from threading import BoundedSemaphore, Lock
from time import monotonic


class RequestLimiter:
    """Cupo y ventana compartidos por proceso; producción requiere coordinación externa."""

    def __init__(self):
        self.slot = BoundedSemaphore(1)
        self.lock = Lock()
        self.attempts: deque[float] = deque()

    def allow(self, limit: int) -> bool:
        now = monotonic()
        with self.lock:
            while self.attempts and self.attempts[0] <= now - 60:
                self.attempts.popleft()
            if len(self.attempts) >= limit:
                return False
            self.attempts.append(now)
            return True


LLM_LIMITER = RequestLimiter()

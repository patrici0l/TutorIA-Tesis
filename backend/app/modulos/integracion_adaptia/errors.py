import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import monotonic
from uuid import uuid4

from fastapi.responses import JSONResponse

from app.modulos.integracion_adaptia.schemas import (
    AdaptiaError,
    AdaptiaFailure,
    ResponseMetadata,
    Tracking,
)

PATH = "/api/v1/tutoria/generate-content"
CORRELATION = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")


@dataclass
class RequestContext:
    request_id: str
    session_id: str
    student_id: str | None = None
    started: float = field(default_factory=monotonic)

    def metadata(self, *, replayed=False):
        return ResponseMetadata(
            timestamp=datetime.now(UTC),
            processing_time_ms=max(0, round((monotonic() - self.started) * 1000)),
            replayed=replayed,
        )

    def tracking(self):
        return Tracking(
            request_id=self.request_id,
            session_id=self.session_id,
            student_id_hash=self.student_id,
        )


def request_context(headers):
    request_id = headers.get("x-request-id", "")
    session_id = headers.get("x-session-id", "")
    return RequestContext(
        request_id if CORRELATION.fullmatch(request_id) else str(uuid4()),
        session_id if CORRELATION.fullmatch(session_id) else str(uuid4()),
    )


class IntegrationError(Exception):
    def __init__(self, status, code, message, *, details=None, headers=None):
        self.status, self.code, self.message = status, code, message
        self.details, self.headers = details, headers or {}
        super().__init__(code)


def failure_response(context: RequestContext, error: IntegrationError):
    payload = AdaptiaFailure(
        error=AdaptiaError(code=error.code, message=error.message, details=error.details),
        metadata=context.metadata(),
        tracking=context.tracking(),
    )
    return JSONResponse(
        payload.model_dump(mode="json"),
        status_code=error.status,
        headers={"Cache-Control": "no-store", "X-Request-ID": context.request_id, **error.headers},
    )

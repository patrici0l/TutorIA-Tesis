from fastapi import HTTPException
from starlette.responses import JSONResponse


class UploadLimitMiddleware:
    """Limita el cuerpo multipart antes de cargarlo o guardarlo en archivos temporales."""

    def __init__(self, app, maximum: int = 11_534_336):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        generation = scope.get("path", "").startswith("/api/v1/content/") and scope.get(
            "path", ""
        ).endswith("/generate")
        if scope["type"] != "http" or (
            not generation
            and scope["path"]
            not in {
                "/api/v1/documents/upload",
                "/api/v1/rag/search",
                "/api/v1/content/prepare",
                "/api/v1/profiles",
            }
        ):
            return await self.app(scope, receive, send)
        maximum = self.maximum if scope["path"] == "/api/v1/documents/upload" else 16_384
        headers = dict(scope.get("headers", []))
        try:
            size = int(headers.get(b"content-length", b"0"))
        except ValueError:
            size = maximum + 1
        if size < 0 or size > maximum:
            return await JSONResponse(
                {"detail": "La solicitud supera el límite de tamaño."}, status_code=413
            )(scope, receive, send)
        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > maximum:
                raise HTTPException(413, "La solicitud supera el límite de tamaño.")
            return message

        await self.app(scope, limited_receive, send)

# Adapta Responses al contrato común sin reintentos ni continuación automática.
from app.modulos.proveedores_ia.servicios.text_rest_provider import TextRestProvider


class OpenAIProvider(TextRestProvider):
    provider = "openai"
    url = "https://api.openai.com/v1/responses"

    def _request(self, request):
        return {"Authorization": "Bearer " + self.settings.openai_api_key.get_secret_value()}, {
            "model": self.settings.llm_model,
            "instructions": request.instructions,
            "input": [{"role": "user", "content": request.prompt}],
            "max_output_tokens": self.settings.llm_max_output_tokens,
            "store": False,
            "stream": False,
            "tools": [],
        }

    def _usage(self, payload):
        raw = payload.get("usage") or {}
        details = raw.get("output_tokens_details") or {}
        cached = raw.get("input_tokens_details") or {}
        return self._safe_usage(
            input_tokens=raw.get("input_tokens"),
            output_tokens=raw.get("output_tokens"),
            total_tokens=raw.get("total_tokens"),
            reasoning_tokens=details.get("reasoning_tokens"),
            cached_input_tokens=cached.get("cached_tokens"),
        )

    def _text(self, payload, usage, latency):
        if payload.get("status") == "incomplete":
            reason = (payload.get("incomplete_details") or {}).get("reason")
            if reason == "max_output_tokens":
                self._fail("llm_incomplete", usage, latency)
            if reason == "content_filter":
                self._fail("llm_blocked", usage, latency)
        if payload.get("status") != "completed" or payload.get("error"):
            raise ValueError()
        output = payload["output"]
        if not isinstance(output, list):
            raise ValueError()
        texts = []
        for item in output:
            if item.get("type") == "reasoning":
                continue
            if (
                item.get("type") != "message"
                or item.get("role") != "assistant"
                or item.get("status") != "completed"
                or not isinstance(item["content"], list)
            ):
                raise ValueError()
            for part in item["content"]:
                if part.get("type") == "refusal":
                    self._fail("llm_blocked", usage, latency)
                if part.get("type") != "output_text" or not isinstance(part.get("text"), str):
                    raise ValueError()
                texts.append(part["text"])
        return "".join(texts)

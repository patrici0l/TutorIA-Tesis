from app.modulos.proveedores_ia.servicios.text_rest_provider import TextRestProvider


class ClaudeProvider(TextRestProvider):
    provider = "claude"
    url = "https://api.anthropic.com/v1/messages"

    def _request(self, request):
        return {
            "x-api-key": self.settings.anthropic_api_key.get_secret_value(),
            "anthropic-version": "2023-06-01",
        }, {
            "model": self.settings.llm_model,
            "system": request.instructions,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": self.settings.llm_max_output_tokens,
            "stream": False,
        }

    def _usage(self, payload):
        raw = payload.get("usage") or {}
        # Messages no informa total_tokens: no inventar una suma que omita escritura de caché.
        return self._safe_usage(
            input_tokens=raw.get("input_tokens"),
            output_tokens=raw.get("output_tokens"),
            cached_input_tokens=raw.get("cache_read_input_tokens"),
        )

    def _text(self, payload, usage, latency):
        reason = payload.get("stop_reason")
        if reason in {"max_tokens", "model_context_window_exceeded"}:
            self._fail("llm_incomplete", usage, latency)
        if reason == "refusal":
            self._fail("llm_blocked", usage, latency)
        if (
            reason != "end_turn"
            or payload.get("type") != "message"
            or payload.get("role") != "assistant"
            or not isinstance(payload["content"], list)
        ):
            raise ValueError()
        texts = []
        for block in payload["content"]:
            if block.get("type") in {"thinking", "redacted_thinking"}:
                continue
            if block.get("type") != "text" or not isinstance(block.get("text"), str):
                raise ValueError()
            texts.append(block["text"])
        return "".join(texts)

import pytest

from app.modulos.contenidos.generation_messages import generation_failure_message


@pytest.mark.parametrize(
    "code, expected",
    [
        ("llm_incomplete", "respuesta incompleta"),
        ("llm_timeout", "tiempo de espera"),
        ("llm_rate_limit", "límite de solicitudes"),
    ],
)
def test_generation_errors_explain_the_recorded_cause(code, expected):
    assert expected in generation_failure_message(code)


def test_unknown_error_never_exposes_provider_details():
    assert "secret-provider-data" not in generation_failure_message("secret-provider-data")

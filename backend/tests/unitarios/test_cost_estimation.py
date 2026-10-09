from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.proveedores_ia.schemas import TokenUsage
from tests.integracion.test_content_trace_database import response


@pytest.mark.parametrize(
    "usage,expected",
    [
        (TokenUsage(input_tokens=20, output_tokens=10), Decimal("0")),
        (TokenUsage(input_tokens=0, output_tokens=0), Decimal("0")),
        (TokenUsage(input_tokens=20, total_tokens=30), None),
        (TokenUsage(output_tokens=10), None),
        (TokenUsage(), None),
    ],
)
def test_conditional_zero_requires_known_input_and_output(usage, expected):
    result = response().model_copy(update={"usage": usage})
    assert CostBasis(requested_model=result.requested_model).estimate(result) == expected


def test_basis_does_not_apply_to_other_model_or_accept_paid_rates():
    assert CostBasis(requested_model="another-model").estimate(response()) is None
    with pytest.raises(ValidationError):
        CostBasis(requested_model="model-test-v1", input_per_million="1")

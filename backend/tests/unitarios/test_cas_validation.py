import httpx
import pytest

from app.configuracion.settings import Settings
from app.modulos.autenticacion.servicios.cas_validation_service import (
    CasValidationError,
    CasValidationService,
)


def xml(email="fictional@est.ups.edu.ec", extra=""):
    return f"""<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:authenticationSuccess><cas:user>fictional-id</cas:user><cas:attributes>
    <cas:email>{email}</cas:email><cas:uid>fictional-id</cas:uid>
    <cas:givenName>Nombre</cas:givenName><cas:sn>Prueba</cas:sn>{extra}
    </cas:attributes></cas:authenticationSuccess></cas:serviceResponse>""".encode()


def test_valid_institutional_attributes():
    identity = CasValidationService(Settings(_env_file=None)).parse(xml())
    assert identity.institutional_id == "fictional-id"
    assert identity.nombre == "Nombre" and identity.rol == "student"


@pytest.mark.parametrize(
    "email", ["fictional@ups.edu.ec", "fictional@est.ups.edu.ec.evil.org", "fictional@example.org"]
)
def test_disallowed_domains(email):
    with pytest.raises(CasValidationError):
        CasValidationService(Settings(_env_file=None)).parse(xml(email))


def test_teacher_domain_only_when_enabled():
    settings = Settings(_env_file=None, auth_allowed_domains="est.ups.edu.ec,ups.edu.ec")
    assert CasValidationService(settings).parse(xml("fictional@ups.edu.ec")).rol == "teacher"


@pytest.mark.parametrize(
    "payload",
    [
        b"<broken",
        b"<serviceResponse/>",
        b'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
        xml(extra="<cas:email>other@est.ups.edu.ec</cas:email>"),
        xml().replace(b"authenticationSuccess", b"authenticationFailure"),
        xml().replace(b"<cas:user>fictional-id</cas:user>", b""),
    ],
)
def test_rejects_invalid_xml_and_ambiguous_attributes(payload):
    with pytest.raises(CasValidationError):
        CasValidationService(Settings(_env_file=None)).parse(payload)


def test_mock_rejected_outside_development():
    with pytest.raises(ValueError):
        Settings(_env_file=None, app_env="production", auth_mode="mock").validate_auth()


def test_cas_requires_complete_https_settings():
    with pytest.raises(ValueError):
        Settings(_env_file=None, auth_mode="cas").validate_auth()


def test_no_mock_redirects_to_external_hosts():
    with pytest.raises(ValueError):
        Settings(_env_file=None, auth_frontend_url="http://evil.example.org").validate_auth()


def test_validation_transport_sends_exact_service_to_configured_server(monkeypatch):
    original_client = httpx.Client

    def respond(request):
        assert str(request.url).startswith("https://sso.example.org/approved-validation?")
        assert request.url.params["ticket"] == "ST-fictional"
        assert (
            request.url.params["service"]
            == "https://tutoria.example.org/api/v1/auth/callback?state=abc"
        )
        return httpx.Response(200, content=xml())

    def factory(**kwargs):
        assert kwargs["follow_redirects"] is False
        assert kwargs["trust_env"] is False
        return original_client(transport=httpx.MockTransport(respond), **kwargs)

    monkeypatch.setattr(httpx, "Client", factory)
    settings = Settings(
        _env_file=None, cas_validate_url="https://sso.example.org/approved-validation"
    )
    result = CasValidationService(settings).validate(
        "ST-fictional", "https://tutoria.example.org/api/v1/auth/callback?state=abc"
    )
    assert result.rol == "student"


@pytest.mark.parametrize("status", [302, 500])
def test_cas_transport_failure_rejects_authentication(monkeypatch, status):
    original_client = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    status, headers={"Location": "https://other.example.org"}
                )
            ),
            **kwargs,
        ),
    )
    settings = Settings(_env_file=None, cas_validate_url="https://sso.example.org/validation")
    with pytest.raises(CasValidationError):
        CasValidationService(settings).validate(
            "ST-fictional", "https://tutoria.example.org/callback"
        )

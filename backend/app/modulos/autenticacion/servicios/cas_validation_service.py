import httpx
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from pydantic import ValidationError

from app.configuracion.settings import Settings
from app.modulos.autenticacion.schemas import InstitutionalIdentity


class CasValidationError(Exception):
    pass


class CasValidationService:
    """Adaptador CAS XML. Los atributos definitivos requieren confirmación de TI."""

    namespace = "{http://www.yale.edu/tp/cas}"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate(self, ticket: str, service_url: str) -> InstitutionalIdentity:
        if not ticket or len(ticket) > 2048:
            raise CasValidationError()
        try:
            # TLS obligatorio, sin redirecciones ni proxies tomados del ambiente.
            with httpx.Client(timeout=8, follow_redirects=False, trust_env=False) as client:
                with client.stream(
                    "GET",
                    self.settings.cas_validate_url,
                    params={
                        self.settings.cas_ticket_parameter: ticket,
                        self.settings.cas_service_parameter: service_url,
                    },
                    headers={"Accept": "application/xml"},
                ) as response:
                    response.raise_for_status()
                    payload = bytearray()
                    for chunk in response.iter_bytes():
                        payload.extend(chunk)
                        if len(payload) > 1_048_576:
                            raise CasValidationError()
            return self.parse(bytes(payload))
        except (httpx.HTTPError, ValueError) as exc:
            raise CasValidationError() from exc

    def parse(self, payload: bytes) -> InstitutionalIdentity:
        try:
            root = ElementTree.fromstring(
                payload, forbid_dtd=True, forbid_entities=True, forbid_external=True
            )
            ns = self.namespace
            if (
                root.tag != ns + "serviceResponse"
                or root.find(ns + "authenticationFailure") is not None
            ):
                raise CasValidationError()
            successes = root.findall(ns + "authenticationSuccess")
            if len(successes) != 1:
                raise CasValidationError()
            success = successes[0]
            username = success.find(ns + "user")
            if username is None or not username.text or not username.text.strip():
                raise CasValidationError()
            attributes = success.find(ns + "attributes")

            def attribute(name: str, required=False):
                if name == "user":
                    return username.text.strip()
                matches = (
                    []
                    if attributes is None
                    else [node for node in attributes if node.tag == ns + name]
                )
                if len(matches) > 1 or (matches and list(matches[0])):
                    raise CasValidationError()
                value = matches[0].text.strip() if matches and matches[0].text else ""
                if required and not value:
                    raise CasValidationError()
                return value

            email = attribute(self.settings.cas_email_attribute, required=True).lower()
            domain = email.rsplit("@", 1)[-1]
            if domain not in self.settings.allowed_domains():
                raise CasValidationError()
            return InstitutionalIdentity(
                institutional_email=email,
                institutional_id=attribute(self.settings.cas_id_attribute) or None,
                nombre=attribute(self.settings.cas_first_name_attribute),
                apellido=attribute(self.settings.cas_last_name_attribute),
                rol="student" if domain == "est.ups.edu.ec" else "teacher",
            )
        except (ElementTree.ParseError, DefusedXmlException, ValidationError, ValueError) as exc:
            raise CasValidationError() from exc

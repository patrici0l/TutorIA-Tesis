from abc import ABC, abstractmethod

from app.modulos.proveedores_ia.schemas import GenerationRequest, GenerationResult


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generar una respuesta completa o levantar ProviderError sin datos sensibles."""

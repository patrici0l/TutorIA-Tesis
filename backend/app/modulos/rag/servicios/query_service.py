import re

QUERY_VERSION = "calculo-alias-v1"


def embedding_query(query: str) -> str:
    """Canonical mathematical terms; preserve the original query in the response."""
    query = re.sub(r"\buna división\b", "un cociente", query, flags=re.IGNORECASE)
    for pattern, concept in (
        (r"\bdivisión\b", "cociente"),
        (r"\bdividir\b", "calcular el cociente de"),
        (r"\bmultiplicación\b", "producto"),
        (r"\bmultiplicar\b", "calcular el producto de"),
    ):
        query = re.sub(pattern, concept, query, flags=re.IGNORECASE)
    return query

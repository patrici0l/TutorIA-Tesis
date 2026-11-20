"""Read-only connector to a fixed Wikimedia host; never follows supplied URLs."""
import hashlib
import json
import re
from datetime import UTC, datetime
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx
from defusedxml import ElementTree
from fastapi import HTTPException
from pydantic import ValidationError

from app.modulos.documentos.external_schemas import ExternalSource, WikiPreview, WikiResult

API_URL = "https://es.wikipedia.org/w/api.php"
USER_AGENT = "TutorIA/0.3 (https://github.com/patrici0l/TutorIA-Tesis; educational prototype)"
MAX_RESPONSE = 2_000_000


class ArticleText(HTMLParser):
    """Keep readable text and TeX alternatives, never execute or return HTML."""
    VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr", "area", "col"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br"}
    OMIT = {"reference", "references", "mw-editsection", "navbox", "infobox", "toc",
            "metadata", "noprint", "mw-math-fallback-image-inline",
            "mw-math-fallback-image-display"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.missing_math = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent_hidden = bool(self.stack and self.stack[-1][1])
        hidden = parent_hidden or tag in {"script", "style", "svg", "noscript"}
        hidden = hidden or bool(set(attrs.get("class", "").split()) & self.OMIT)
        if not hidden:
            if tag in self.BLOCK:
                self.parts.append("\n")
            if tag == "math":
                tex = attrs.get("alttext", "").strip()
                if not tex:
                    self.missing_math = True
                else:
                    self.parts.append(" $" + tex + "$ ")
                hidden = True
            elif tag == "sup":
                self.parts.append("^(")
            elif tag == "sub":
                self.parts.append("_(")
            elif tag in {"td", "th"}:
                self.parts.append(" | ")
        if tag not in self.VOID:
            self.stack.append((tag, hidden))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                hidden = self.stack[i][1]
                del self.stack[i:]
                if not hidden and tag in self.BLOCK:
                    self.parts.append("\n")
                if not hidden and tag in {"sup", "sub"}:
                    self.parts.append(")")
                break

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.parts.append(data)

    def text(self):
        lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip()
                 for line in "".join(self.parts).split("\n")]
        return "\n\n".join(line for line in lines if line)


def preserve_math(html):
    """Convert supported MathML structure to TeX; reject unknown constructs explicitly."""
    def convert(node, depth=0):
        if depth > 60:
            raise ValueError("math_depth")
        tag = node.tag.rsplit("}", 1)[-1]
        children = [convert(child, depth + 1) for child in node]
        if tag in {"math", "mrow", "mstyle", "mtd", "semantics"}:
            return " ".join(children)
        if tag in {"mi", "mn", "mo"}:
            token = (node.text or "").strip()
            return token.replace("{", r"\{").replace("}", r"\}")
        if tag == "mtext":
            token = (node.text or "").replace("\\", r"\backslash ")
            for char in ["{", "}", "%", "#", "&", "_", "$"]:
                token = token.replace(char, "\\" + char)
            return r"\text{" + token + "}"
        if tag in {"mspace", "annotation"}:
            return " "
        if tag == "mfrac" and len(children) == 2:
            return r"\frac{" + children[0] + "}{" + children[1] + "}"
        if tag in {"msup", "msub"} and len(children) == 2:
            operator = "^" if tag == "msup" else "_"
            return "{" + children[0] + "}" + operator + "{" + children[1] + "}"
        if tag == "msubsup" and len(children) == 3:
            return "{" + children[0] + "}_{" + children[1] + "}^{" + children[2] + "}"
        if tag == "msqrt":
            return r"\sqrt{" + " ".join(children) + "}"
        if tag == "mroot" and len(children) == 2:
            return r"\sqrt[" + children[1] + "]{" + children[0] + "}"
        if tag in {"munder", "mover"} and len(children) == 2:
            command = r"\underset" if tag == "munder" else r"\overset"
            return command + "{" + children[1] + "}{" + children[0] + "}"
        if tag == "munderover" and len(children) == 3:
            inner = r"\underset{" + children[1] + "}{" + children[0] + "}"
            return r"\overset{" + children[2] + "}{" + inner + "}"
        if tag == "mtr":
            return " & ".join(children)
        if tag == "mtable":
            return r"\begin{matrix}" + r" \\ ".join(children) + r"\end{matrix}"
        raise ValueError("unsupported_math")

    def replace(match):
        try:
            node = ElementTree.fromstring(match.group(0))
            tex = node.attrib.get("alttext") or convert(node)
            if not tex.strip():
                raise ValueError("empty_math")
            return '<math alttext="' + escape(tex, quote=True) + '"></math>'
        except Exception:
            raise HTTPException(422, "Hay fórmulas no compatibles. Usa otra fuente.") from None

    return re.sub(r"<math\b[^>]*>.*?</math>", replace, html, flags=re.DOTALL)


class MediaWikiService:
    def __init__(self, transport=None):
        self.transport = transport

    def fetch(self, params):
        params = {"format": "json", "formatversion": 2, "maxlag": 5, **params}
        try:
            with httpx.Client(timeout=12, follow_redirects=False, transport=self.transport,
                              headers={"User-Agent": USER_AGENT}) as client:
                with client.stream("GET", API_URL, params=params) as response:
                    if response.status_code == 429:
                        raise HTTPException(503, "Wikipedia está ocupada. Inténtalo más tarde.")
                    if response.status_code != 200:
                        raise HTTPException(503, "Wikipedia no está disponible en este momento.")
                    payload = bytearray()
                    for part in response.iter_bytes():
                        payload.extend(part)
                        if len(payload) > MAX_RESPONSE:
                            raise HTTPException(422, "El artículo supera el tamaño admitido.")
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError()
            if "error" in data:
                code = data["error"].get("code")
                if code in {"missingtitle", "nosuchrevid", "missingcontent", "invalidpageid"}:
                    raise HTTPException(404, "El artículo o su versión ya no están disponibles.")
                raise HTTPException(503, "Wikipedia no pudo completar la consulta.")
            return data
        except httpx.TimeoutException:
            raise HTTPException(504, "Wikipedia tardó demasiado. Vuelve a intentarlo.") from None
        except (httpx.HTTPError, ValueError, TypeError):
            raise HTTPException(503, "No se pudo leer la respuesta de Wikipedia.") from None

    def search(self, query):
        data = self.fetch({"action": "query", "list": "search", "srsearch": query,
                           "srnamespace": 0, "srlimit": 5, "srprop": ""})
        try:
            return [WikiResult(page_id=row["pageid"], title=row["title"])
                    for row in data["query"]["search"] if row["ns"] == 0]
        except (KeyError, TypeError, ValidationError):
            raise HTTPException(503, "La búsqueda devolvió datos incompletos.") from None

    def preview(self, page_id, revision_id=None):
        selector = {"revids": revision_id} if revision_id else {"pageids": page_id}
        metadata = self.fetch({"action": "query", "prop": "revisions",
                               "rvprop": "ids|timestamp", "meta": "siteinfo",
                               "siprop": "rightsinfo", **selector})
        try:
            page = metadata["query"]["pages"][0]
            if page.get("missing") or page.get("ns") != 0 or page["pageid"] != page_id:
                raise HTTPException(404, "No se encontró un artículo válido.")
            revision = page["revisions"][0]
            rid = revision["revid"]
            if revision_id and rid != revision_id:
                raise HTTPException(409, "La versión no coincide. Revisa el artículo otra vez.")
            rights = metadata["query"]["rightsinfo"]
            license_url = rights["url"]
            if license_url.startswith("//"):
                license_url = "https:" + license_url
            if urlparse(license_url).scheme != "https" or not rights["text"]:
                raise ValueError()
            parsed = self.fetch({"action": "parse", "oldid": rid,
                                 "prop": "text|wikitext|revid", "disableeditsection": 1})
            article = parsed["parse"]
            if article["revid"] != rid or article["pageid"] != page_id:
                raise HTTPException(409, "Wikipedia devolvió otra versión. Repite la revisión.")
            parser = ArticleText()
            parser.feed(preserve_math(article["text"]))
            parser.close()
            text = parser.text()
            if parser.missing_math:
                raise HTTPException(422, "Hay fórmulas sin texto recuperable. Usa otra fuente.")
            if len(text) < 80 or len(text) > 100_000:
                raise HTTPException(422, "El artículo tiene muy poco texto o supera el límite.")
            snapshot = json.dumps({"metadata": metadata, "article": parsed},
                                  ensure_ascii=False, sort_keys=True).encode("utf-8")
            source = ExternalSource(
                page_id=page_id, revision_id=rid, title=article["title"],
                url=f"https://es.wikipedia.org/w/index.php?oldid={rid}",
                revision_at=revision["timestamp"], retrieved_at=datetime.now(UTC),
                license_name=rights["text"], license_url=license_url,
                attribution=("Colaboradores de Wikipedia en español; "
                             "consultar historial del artículo."),
                text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                snapshot_sha256=hashlib.sha256(snapshot).hexdigest(),
            )
            return WikiPreview(source=source, text=text, warnings=[
                "Se importará texto adaptado del artículo; no imágenes ni contenido multimedia.",
                "Revisa fórmulas, tablas y pertinencia antes de habilitarlo como fuente.",
            ]), snapshot
        except (KeyError, IndexError, TypeError, ValueError, ValidationError):
            raise HTTPException(503, "El artículo no contiene los datos necesarios.") from None

"""Bounded text extraction and reproducible character-based segmentation.

Offsets always refer to the normalized source unit. Chunks never cross a page
or paragraph, so their source references remain meaningful without a tokenizer.
This service does not perform OCR or execute document content.
"""

import io
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from defusedxml import ElementTree
from pypdf import PdfReader

EXTRACTOR_VERSION = "text-v1"
MAX_TEXT_CHARS = 500_000
MAX_CHUNKS = 1000
MAX_PAGES = 200
MAX_PAYLOAD_BYTES = 10_485_760
MAX_DOCX_EXPANDED_BYTES = 52_428_800
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


@dataclass(frozen=True, slots=True)
class TextUnit:
    source_kind: str
    source_index: int
    text: str


@dataclass(frozen=True, slots=True)
class TextChunk:
    position: int
    source_kind: str
    source_index: int
    char_start: int
    char_end: int
    text: str


class ExtractionError(Exception):
    """Only a stable code is exposed; parser errors may contain source data."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class DocumentTextService:
    def extract(self, payload: bytes, mime_type: str) -> list[TextUnit]:
        if not isinstance(payload, bytes) or not payload:
            raise ExtractionError("invalid_document")
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ExtractionError("extraction_limit")
        extractors = {
            "application/pdf": self._extract_pdf,
            MIME_DOCX: self._extract_docx,
            "text/plain": self._extract_txt,
        }
        extractor = extractors.get(mime_type)
        if extractor is None:
            raise ExtractionError("unsupported_document")
        try:
            units = extractor(payload)
        except ExtractionError:
            raise
        except Exception:
            raise ExtractionError("invalid_document") from None
        if not units:
            raise ExtractionError("empty_text")
        return units

    def chunk(
        self,
        units: list[TextUnit],
        chunk_chars: int = 1000,
        chunk_overlap: int = 150,
    ) -> list[TextChunk]:
        if (
            type(chunk_chars) is not int
            or type(chunk_overlap) is not int
            or chunk_chars < 1
            or not 0 <= chunk_overlap < chunk_chars
        ):
            raise ValueError("Invalid character segmentation settings")
        chunks: list[TextChunk] = []
        total_chars = 0
        for unit in units:
            if (
                unit.source_kind not in {"page", "paragraph"}
                or type(unit.source_index) is not int
                or unit.source_index < 1
                or not isinstance(unit.text, str)
                or not unit.text.strip()
            ):
                raise ExtractionError("invalid_document")
            total_chars += len(unit.text)
            if total_chars > MAX_TEXT_CHARS:
                raise ExtractionError("extraction_limit")
            start = 0
            while start < len(unit.text):
                end = min(start + chunk_chars, len(unit.text))
                if end < len(unit.text):
                    # A cut must leave at least one new character after overlap.
                    lower = start + max(chunk_overlap + 1, int(chunk_chars * 0.6))
                    preferred = self._preferred_end(unit.text, lower, end)
                    if preferred is not None:
                        end = preferred
                if len(chunks) >= MAX_CHUNKS:
                    raise ExtractionError("extraction_limit")
                chunks.append(
                    TextChunk(
                        position=len(chunks),
                        source_kind=unit.source_kind,
                        source_index=unit.source_index,
                        char_start=start,
                        char_end=end,
                        text=unit.text[start:end],
                    )
                )
                if end == len(unit.text):
                    break
                start = end - chunk_overlap
        if not chunks:
            raise ExtractionError("empty_text")
        return chunks

    @staticmethod
    def _preferred_end(text: str, lower: int, upper: int) -> int | None:
        window = text[lower:upper]
        sentence_breaks = list(re.finditer(r"(?<=[.!?;])(?:[ \t]+|\n)|\n", window))
        if sentence_breaks:
            return lower + sentence_breaks[-1].end()
        word_breaks = list(re.finditer(r"[ \t]+", window))
        if word_breaks:
            return lower + word_breaks[-1].end()
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
        lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _add_unit(
        self,
        units: list[TextUnit],
        source_kind: str,
        source_index: int,
        text: str,
        total_chars: int,
    ) -> int:
        # Bound both raw extraction and normalized output. Normalization cannot
        # conceal excessive whitespace or decomposed Unicode input.
        if total_chars + len(text) > MAX_TEXT_CHARS:
            raise ExtractionError("extraction_limit")
        if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
            raise ExtractionError("invalid_document")
        normalized = self._normalize(text)
        total_chars += max(len(text), len(normalized))
        if total_chars > MAX_TEXT_CHARS:
            raise ExtractionError("extraction_limit")
        if normalized:
            if len(units) >= MAX_CHUNKS:
                raise ExtractionError("extraction_limit")
            units.append(TextUnit(source_kind, source_index, normalized))
        return total_chars

    def _extract_txt(self, payload: bytes) -> list[TextUnit]:
        text = payload.decode("utf-8-sig")
        if len(text) > MAX_TEXT_CHARS:
            raise ExtractionError("extraction_limit")
        if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
            raise ExtractionError("invalid_document")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = re.split(r"\n[ \t]*\n+", text)
        units: list[TextUnit] = []
        total_chars = 0
        for index, paragraph in enumerate(paragraphs, start=1):
            total_chars = self._add_unit(units, "paragraph", index, paragraph, total_chars)
        return units

    def _extract_pdf(self, payload: bytes) -> list[TextUnit]:
        if not payload.startswith(b"%PDF-"):
            raise ExtractionError("invalid_document")
        reader = PdfReader(io.BytesIO(payload), strict=True)
        if reader.is_encrypted or not reader.pages:
            raise ExtractionError("invalid_document")
        if len(reader.pages) > MAX_PAGES:
            raise ExtractionError("extraction_limit")
        units: list[TextUnit] = []
        total_chars = 0
        for index, page in enumerate(reader.pages, start=1):
            total_chars = self._add_unit(
                units, "page", index, page.extract_text() or "", total_chars
            )
        return units

    def _extract_docx(self, payload: bytes) -> list[TextUnit]:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if len(entries) > 2000:
                raise ExtractionError("extraction_limit")
            if len(set(names)) != len(names) or not {
                "[Content_Types].xml",
                "word/document.xml",
            }.issubset(names):
                raise ExtractionError("invalid_document")
            if sum(entry.file_size for entry in entries) > MAX_DOCX_EXPANDED_BYTES:
                raise ExtractionError("extraction_limit")
            document = None
            styles = None
            for entry in entries:
                path = PurePosixPath(entry.filename)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in entry.filename
                    or entry.flag_bits & 1
                ):
                    raise ExtractionError("invalid_document")
                if (
                    entry.file_size > MAX_PAYLOAD_BYTES
                    or entry.file_size / max(1, entry.compress_size) > 200
                ):
                    raise ExtractionError("extraction_limit")
                lower = entry.filename.lower()
                if any(value in lower for value in ("vbaproject", "activex/", "embeddings/")):
                    raise ExtractionError("invalid_document")
                if lower.endswith((".xml", ".rels")):
                    root = ElementTree.fromstring(
                        archive.read(entry),
                        forbid_dtd=True,
                        forbid_entities=True,
                        forbid_external=True,
                    )
                    if lower.endswith(".rels") and any(
                        node.attrib.get("TargetMode") == "External" for node in root
                    ):
                        raise ExtractionError("invalid_document")
                    if entry.filename == "[Content_Types].xml" and not any(
                        node.attrib.get("PartName") == "/word/document.xml"
                        and node.attrib.get("ContentType")
                        == (
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document.main+xml"
                        )
                        for node in root
                    ):
                        raise ExtractionError("invalid_document")
                    if entry.filename == "word/document.xml":
                        document = root
                    elif entry.filename == "word/styles.xml":
                        styles = root
            if document is None or document.tag != f"{{{WORD_NS}}}document":
                raise ExtractionError("invalid_document")
            if any(node.tag.startswith(f"{{{MATH_NS}}}") for node in document.iter()):
                # Concatenating OMML tokens can turn x^2 into x2. Do not create
                # a misleading corpus until formula conversion is supported.
                raise ExtractionError("unsupported_document")
            self._reject_styled_vertical_alignment(document, styles)
            units: list[TextUnit] = []
            total_chars = 0
            for index, paragraph in enumerate(document.iter(f"{{{WORD_NS}}}p"), start=1):
                total_chars = self._add_unit(
                    units, "paragraph", index, self._paragraph_text(paragraph), total_chars
                )
            return units

    def _paragraph_text(self, paragraph) -> str:
        def text_of(node) -> str:
            if node is not paragraph and node.tag == f"{{{WORD_NS}}}p":
                # Nested text boxes receive their own paragraph reference.
                return ""
            if node.tag == f"{{{WORD_NS}}}t":
                return node.text or ""
            if node.tag == f"{{{WORD_NS}}}tab":
                return "\t"
            if node.tag in {f"{{{WORD_NS}}}br", f"{{{WORD_NS}}}cr"}:
                return "\n"
            if node.tag == f"{{{WORD_NS}}}noBreakHyphen":
                return "\u2011"
            if node.tag == f"{{{WORD_NS}}}softHyphen":
                return "\u00ad"
            text = "".join(text_of(child) for child in node)
            if node.tag == f"{{{WORD_NS}}}r":
                alignment = node.find(f"{{{WORD_NS}}}rPr/{{{WORD_NS}}}vertAlign")
                if alignment is not None and text:
                    value = alignment.attrib.get(f"{{{WORD_NS}}}val")
                    if value in {"superscript", "subscript"}:
                        marker = "^" if value == "superscript" else "_"
                        text = f"{marker}({text})"
            return text

        return text_of(paragraph)

    @staticmethod
    def _reject_styled_vertical_alignment(document, styles):
        if styles is None:
            return
        if styles.tag != f"{{{WORD_NS}}}styles":
            raise ExtractionError("invalid_document")
        value_attribute = f"{{{WORD_NS}}}val"
        default_alignment = styles.find(
            f"{{{WORD_NS}}}docDefaults/{{{WORD_NS}}}rPrDefault/"
            f"{{{WORD_NS}}}rPr/{{{WORD_NS}}}vertAlign"
        )
        if default_alignment is not None and default_alignment.get(value_attribute) in {
            "superscript",
            "subscript",
        }:
            raise ExtractionError("unsupported_document")
        definitions = {}
        references = {
            node.get(value_attribute)
            for node in document.iter()
            if node.tag in {f"{{{WORD_NS}}}rStyle", f"{{{WORD_NS}}}pStyle"}
        }
        for style in styles.findall(f"{{{WORD_NS}}}style"):
            identifier = style.get(f"{{{WORD_NS}}}styleId")
            if not identifier or identifier in definitions:
                raise ExtractionError("invalid_document")
            definitions[identifier] = style
            if style.get(f"{{{WORD_NS}}}default") in {"1", "true"}:
                references.add(identifier)
        for reference in references:
            visited = set()
            while reference in definitions:
                if reference in visited or len(visited) >= 100:
                    raise ExtractionError("invalid_document")
                visited.add(reference)
                style = definitions[reference]
                alignment = style.find(f"{{{WORD_NS}}}rPr/{{{WORD_NS}}}vertAlign")
                if alignment is not None and alignment.get(value_attribute) in {
                    "superscript",
                    "subscript",
                }:
                    # The complete Word style cascade is intentionally deferred.
                    raise ExtractionError("unsupported_document")
                based_on = style.find(f"{{{WORD_NS}}}basedOn")
                reference = based_on.get(value_attribute) if based_on is not None else None

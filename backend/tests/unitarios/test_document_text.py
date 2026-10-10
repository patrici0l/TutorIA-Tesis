import io
import zipfile

import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.modulos.rag.servicios import document_text_service as text_module
from app.modulos.rag.servicios.document_text_service import (
    MAX_CHUNKS,
    MAX_PAYLOAD_BYTES,
    MAX_TEXT_CHARS,
    MIME_DOCX,
    DocumentTextService,
    ExtractionError,
    TextUnit,
)


def pdf(pages: list[str | None], encrypted: bool = False) -> bytes:
    writer = PdfWriter()
    for text in pages:
        page = writer.add_blank_page(width=612, height=792)
        if text is not None:
            font = DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }
            )
            page[NameObject("/Resources")] = DictionaryObject(
                {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
            )
            content = DecodedStreamObject()
            content.set_data(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii"))
            page[NameObject("/Contents")] = writer._add_object(content)
    if encrypted:
        writer.encrypt("fictitious-test-password")
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def docx(body: str, extra: tuple[str, bytes | str] | None = None) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/word/document.xml" ContentType="'
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
            f"<w:body>{body}</w:body></w:document>",
        )
        if extra:
            archive.writestr(*extra)
    return stream.getvalue()


def assert_code(code: str, payload: bytes, mime_type: str):
    with pytest.raises(ExtractionError) as caught:
        DocumentTextService().extract(payload, mime_type)
    assert caught.value.code == code
    assert str(caught.value) == code


def test_txt_normalization_preserves_mathematics_and_paragraphs():
    payload = (
        "\ufeff  Ca\u0301lculo\t x² − y₁ = ∫ f(x) dx\r\nsegunda línea  \r\n\r\n Otro párrafo. "
    ).encode("utf-8")
    assert DocumentTextService().extract(payload, "text/plain") == [
        TextUnit("paragraph", 1, "Cálculo x² − y₁ = ∫ f(x) dx\nsegunda línea"),
        TextUnit("paragraph", 2, "Otro párrafo."),
    ]


def test_pdf_page_references_skip_empty_pages_without_renumbering():
    units = DocumentTextService().extract(
        pdf(["First page.", None, "Third page."]), "application/pdf"
    )
    assert units == [
        TextUnit("page", 1, "First page."),
        TextUnit("page", 3, "Third page."),
    ]


def test_docx_runs_tables_and_blank_paragraphs_keep_document_order():
    payload = docx(
        "<w:p><w:r><w:t>Ca\u0301lculo </w:t></w:r>"
        "<w:r><w:t>x²</w:t><w:tab/><w:t>∫ f(x) dx</w:t><w:br/><w:t>Continuación.</w:t></w:r></w:p>"
        "<w:p/>"
        "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Celda uno.</w:t></w:r></w:p></w:tc>"
        "<w:tc><w:p><w:r><w:t>Celda dos.</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
    )
    assert DocumentTextService().extract(payload, MIME_DOCX) == [
        TextUnit("paragraph", 1, "Cálculo x² ∫ f(x) dx\nContinuación."),
        TextUnit("paragraph", 3, "Celda uno."),
        TextUnit("paragraph", 4, "Celda dos."),
    ]


def test_docx_formatted_exponents_and_subscripts_do_not_become_plain_digits():
    payload = docx(
        "<w:p><w:r><w:t>x</w:t></w:r>"
        '<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>2</w:t></w:r>'
        "<w:r><w:t> + a</w:t></w:r>"
        '<w:r><w:rPr><w:vertAlign w:val="subscript"/></w:rPr><w:t>n</w:t></w:r></w:p>'
    )
    assert DocumentTextService().extract(payload, MIME_DOCX) == [
        TextUnit("paragraph", 1, "x^(2) + a_(n)")
    ]


def test_docx_office_math_is_rejected_instead_of_flattening_a_fraction():
    payload = docx(
        "<w:p><w:r><w:t>Fracción: </w:t></w:r><m:oMath><m:f>"
        "<m:num><m:r><m:t>1</m:t></m:r></m:num>"
        "<m:den><m:r><m:t>2</m:t></m:r></m:den></m:f></m:oMath></w:p>"
    )
    assert_code("unsupported_document", payload, MIME_DOCX)


@pytest.mark.parametrize("reference", ["rStyle", "pStyle"])
def test_docx_referenced_vertical_styles_are_not_silently_flattened(reference):
    property_tag = "rPr" if reference == "rStyle" else "pPr"
    properties = f'<w:{property_tag}><w:{reference} w:val="Derived"/></w:{property_tag}>'
    body = (
        f"<w:p><w:r>{properties}<w:t>2</w:t></w:r></w:p>"
        if reference == "rStyle"
        else f"<w:p>{properties}<w:r><w:t>2</w:t></w:r></w:p>"
    )
    styles = (
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:styleId="Base"><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>'
        '<w:style w:styleId="Derived"><w:basedOn w:val="Base"/></w:style></w:styles>'
    )
    assert_code("unsupported_document", docx(body, ("word/styles.xml", styles)), MIME_DOCX)


def test_docx_unused_footnote_style_does_not_prevent_text_extraction():
    styles = (
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:styleId="FootnoteReference">'
        '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style></w:styles>'
    )
    units = DocumentTextService().extract(
        docx("<w:p><w:r><w:t>Texto habitual.</w:t></w:r></w:p>", ("word/styles.xml", styles)),
        MIME_DOCX,
    )
    assert units == [TextUnit("paragraph", 1, "Texto habitual.")]


def test_docx_default_vertical_style_is_reported_as_unsupported():
    styles = (
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:vertAlign w:val="superscript"/>'
        "</w:rPr></w:rPrDefault></w:docDefaults></w:styles>"
    )
    assert_code(
        "unsupported_document",
        docx("<w:p><w:r><w:t>2</w:t></w:r></w:p>", ("word/styles.xml", styles)),
        MIME_DOCX,
    )


def test_docx_text_boxes_are_not_extracted_twice():
    payload = docx(
        "<w:p><w:r><w:t>Exterior.</w:t></w:r><w:txbxContent>"
        "<w:p><w:r><w:t>Interior.</w:t></w:r></w:p></w:txbxContent></w:p>"
    )
    assert DocumentTextService().extract(payload, MIME_DOCX) == [
        TextUnit("paragraph", 1, "Exterior."),
        TextUnit("paragraph", 2, "Interior."),
    ]


def test_chunks_exact_offsets_overlap_and_full_coverage_with_source_boundaries():
    units = [
        TextUnit(
            "page", 2, "Primera oración. Segunda oración más extensa con x² y ∫ f(x) dx. Fin."
        ),
        TextUnit("page", 5, "Una página diferente y bastante más corta."),
    ]
    chunks = DocumentTextService().chunk(units, chunk_chars=30, chunk_overlap=7)
    assert [chunk.position for chunk in chunks] == list(range(len(chunks)))
    for unit in units:
        matching = [chunk for chunk in chunks if chunk.source_index == unit.source_index]
        assert matching[0].char_start == 0
        assert matching[-1].char_end == len(unit.text)
        rebuilt = matching[0].text
        for previous, current in zip(matching, matching[1:]):
            assert current.char_start == previous.char_end - 7
            assert previous.text[-7:] == current.text[:7]
            rebuilt += current.text[7:]
        assert rebuilt == unit.text
        for chunk in matching:
            assert chunk.source_kind == "page"
            assert chunk.text == unit.text[chunk.char_start : chunk.char_end]
            assert 0 < len(chunk.text) <= 30


def test_chunking_progresses_for_unbroken_text_and_near_full_overlap():
    text = "abcdefghijklmnop"
    chunks = DocumentTextService().chunk([TextUnit("paragraph", 1, text)], 5, 4)
    assert [(chunk.char_start, chunk.char_end) for chunk in chunks] == [
        (index, index + 5) for index in range(12)
    ]


def test_sentence_boundary_is_preferred_to_an_interior_word():
    text = "Uno dos tres cuatro. Cinco seis siete ocho nueve."
    chunks = DocumentTextService().chunk([TextUnit("paragraph", 1, text)], 30, 5)
    assert chunks[0].text == "Uno dos tres cuatro. "


@pytest.mark.parametrize("size,overlap", [(0, 0), (10, 10), (10, -1), (True, 0)])
def test_invalid_segmentation_configuration_is_rejected(size, overlap):
    with pytest.raises(ValueError):
        DocumentTextService().chunk([TextUnit("paragraph", 1, "Texto.")], size, overlap)


@pytest.mark.parametrize(
    "payload,mime_type,code",
    [
        (b"", "text/plain", "invalid_document"),
        (b"\xff", "text/plain", "invalid_document"),
        (b"x\x00y", "text/plain", "invalid_document"),
        (b"  \n\t\n", "text/plain", "empty_text"),
        (b"fake", "application/pdf", "invalid_document"),
        (pdf([None]), "application/pdf", "empty_text"),
        (pdf(["Text"], encrypted=True), "application/pdf", "invalid_document"),
        (b"not a zip", MIME_DOCX, "invalid_document"),
        (docx("<w:p/>"), MIME_DOCX, "empty_text"),
        (b"Text", "application/octet-stream", "unsupported_document"),
    ],
)
def test_invalid_or_unextractable_documents_have_safe_codes(payload, mime_type, code):
    assert_code(code, payload, mime_type)


def test_extraction_limits_payload_text_and_pdf_pages(monkeypatch):
    assert_code("extraction_limit", b"x" * (MAX_PAYLOAD_BYTES + 1), "text/plain")
    assert_code("extraction_limit", b"x" * (MAX_TEXT_CHARS + 1), "text/plain")
    monkeypatch.setattr(text_module, "MAX_PAGES", 2)
    assert_code("extraction_limit", pdf(["One", "Two", "Three"]), "application/pdf")


def test_docx_expansion_limits_and_external_relationships():
    assert_code("extraction_limit", docx("<w:p/>", ("word/large.txt", b"x" * 1_000_000)), MIME_DOCX)
    assert_code(
        "invalid_document",
        docx(
            "<w:p/>",
            (
                "word/_rels/document.xml.rels",
                '<Relationships><Relationship TargetMode="External" Target="https://example.org"/>'
                "</Relationships>",
            ),
        ),
        MIME_DOCX,
    )
    assert_code("invalid_document", docx("<w:p/>", ("../escape", b"bad")), MIME_DOCX)


def test_docx_entities_are_not_expanded():
    payload = docx("<w:p/>")
    source = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(payload)) as original, zipfile.ZipFile(source, "w") as altered:
        for entry in original.infolist():
            data = original.read(entry)
            if entry.filename == "word/document.xml":
                data = b'<!DOCTYPE root [<!ENTITY source "private-source">]>' + data
            altered.writestr(entry.filename, data)
    assert_code("invalid_document", source.getvalue(), MIME_DOCX)


def test_chunk_limits_apply_to_total_chars_and_total_units():
    service = DocumentTextService()
    with pytest.raises(ExtractionError, match="extraction_limit"):
        service.chunk([TextUnit("paragraph", 1, "x" * (MAX_TEXT_CHARS + 1))])
    units = [TextUnit("paragraph", index + 1, "text") for index in range(MAX_CHUNKS + 1)]
    with pytest.raises(ExtractionError, match="extraction_limit"):
        service.chunk(units)
    with pytest.raises(ExtractionError, match="empty_text"):
        service.chunk([])


def test_extraction_limits_short_units_before_allocating_too_many():
    assert_code("extraction_limit", b"x\n\n" * (MAX_CHUNKS + 1), "text/plain")


def test_control_characters_from_docx_cannot_reach_postgresql():
    payload = docx("<w:p><w:r><w:t>Contenido&#x7F;</w:t></w:r></w:p>")
    assert_code("invalid_document", payload, MIME_DOCX)


def test_nfc_expansion_is_also_bounded(monkeypatch):
    monkeypatch.setattr(text_module, "MAX_TEXT_CHARS", 4)
    # U+0344 is canonically decomposed into two marks even under NFC.
    assert_code("extraction_limit", "\u0344\u0344\u0344".encode(), "text/plain")

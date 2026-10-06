import io
import unicodedata
import zipfile
from pathlib import PurePosixPath

from defusedxml import ElementTree
from fastapi import HTTPException
from pypdf import PdfReader


class DocumentValidationService:
    formats = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }

    def validate(self, filename: str, mime_type: str, payload: bytes) -> tuple[str, str]:
        if not payload:
            raise HTTPException(422, "El archivo está vacío.")
        if (
            not filename
            or len(filename) > 180
            or filename in {".", ".."}
            or any(c in filename for c in "/\\:")
            or any(unicodedata.category(c).startswith("C") for c in filename)
        ):
            raise HTTPException(422, "El nombre del archivo no es válido.")
        extension = PurePosixPath(filename).suffix.lower()
        expected = self.formats.get(extension)
        if not expected or mime_type.split(";", 1)[0].strip().lower() != expected:
            raise HTTPException(
                415, "Formato no permitido o tipo MIME incompatible. Usa PDF, DOCX o TXT."
            )
        try:
            if extension == ".pdf":
                if not payload.startswith(b"%PDF-"):
                    raise ValueError()
                reader = PdfReader(io.BytesIO(payload), strict=True)
                if reader.is_encrypted or not reader.pages:
                    raise ValueError()
                root = reader.trailer["/Root"]
                # No se aceptan acciones automáticas, scripts ni archivos adjuntos.
                if any(key in root for key in ("/OpenAction", "/AA")):
                    raise ValueError()
                names = root.get("/Names")
                if names and any(
                    key in names.get_object() for key in ("/JavaScript", "/EmbeddedFiles")
                ):
                    raise ValueError()
                for page in reader.pages:
                    if page.get("/AA"):
                        raise ValueError()
                    for reference in page.get("/Annots", []):
                        annotation = reference.get_object()
                        if annotation.get("/A") or annotation.get("/AA") or annotation.get("/FS"):
                            raise ValueError()
            elif extension == ".docx":
                self.validate_docx(payload)
            else:
                text = payload.decode("utf-8-sig")
                if not text.strip() or any(
                    unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text
                ):
                    raise ValueError()
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                422, "Archivo inválido, cifrado o con contenido activo no permitido."
            ) from None
        return filename, expected

    def validate_docx(self, payload: bytes):
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if len(entries) > 2000 or len(set(names)) != len(names):
                raise ValueError()
            required = {"[Content_Types].xml", "word/document.xml"}
            if not required.issubset(names) or sum(e.file_size for e in entries) > 52_428_800:
                raise ValueError()
            for entry in entries:
                path = PurePosixPath(entry.filename)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in entry.filename
                    or entry.flag_bits & 1
                    or entry.file_size > 10_485_760
                    or entry.file_size / max(1, entry.compress_size) > 200
                ):
                    raise ValueError()
                lower = entry.filename.lower()
                if any(value in lower for value in ("vbaproject", "activex/", "embeddings/")):
                    raise ValueError()
                if lower.endswith((".xml", ".rels")):
                    root = ElementTree.fromstring(
                        archive.read(entry),
                        forbid_dtd=True,
                        forbid_entities=True,
                        forbid_external=True,
                    )
                    if lower.endswith(".rels") and any(
                        n.attrib.get("TargetMode") == "External" for n in root
                    ):
                        raise ValueError()
                    if entry.filename == "[Content_Types].xml":
                        valid = any(
                            n.attrib.get("PartName") == "/word/document.xml"
                            and n.attrib.get("ContentType")
                            == (
                                "application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document.main+xml"
                            )
                            for n in root
                        )
                        if not valid:
                            raise ValueError()
                    if (
                        entry.filename == "word/document.xml"
                        and root.tag
                        != "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document"
                    ):
                        raise ValueError()

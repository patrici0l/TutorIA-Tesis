# Dependencias de terceros

El inventario exacto de versiones está en frontend/package-lock.json y backend/requirements/*.txt. Los textos de licencia se conservan en los paquetes distribuidos. La compilación de Angular extrae las licencias de su bundle en dist/tutoria/3rdpartylicenses.txt.

Dependencias principales: Angular, RxJS, TypeScript, FastAPI, Pydantic, SQLAlchemy, psycopg, Alembic, Uvicorn, HTTPX, defusedxml, email-validator, python-multipart y pypdf. Infraestructura: Python, Node.js, nginx, PostgreSQL y pgvector. Herramientas de pruebas: pytest, HTTPX, Ruff y Vitest.

Indexación local: ONNX Runtime, tokenizers, NumPy y cliente Python pgvector; sus dependencias transitivas también están fijadas en requirements/base.txt. Se utiliza intfloat/multilingual-e5-small, revisión 614241f622f53c4eeff9890bdc4f31cfecc418b3. La [ficha oficial de esa revisión](https://huggingface.co/intfloat/multilingual-e5-small/blob/614241f622f53c4eeff9890bdc4f31cfecc418b3/README.md) declara licencia MIT. Los pesos/tokenizer se descargan explícitamente a un volumen local y no forman parte del repositorio ni de las imágenes. Conservar los avisos/licencias correspondientes antes de redistribuirlos; esta declaración no concede licencia al código propio ni autoriza el uso de corpus institucional.

Antes de una distribución externa se debe completar el inventario legal de dependencias transitivas y de las imágenes utilizadas. Este listado inicial no sustituye sus textos de licencia ni afirma que todas tengan la misma licencia.

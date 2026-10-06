# Dependencias de terceros

El inventario exacto de versiones está en frontend/package-lock.json y backend/requirements/*.txt. Los textos de licencia se conservan en los paquetes distribuidos. La compilación de Angular extrae las licencias de su bundle en dist/tutoria/3rdpartylicenses.txt.

Dependencias principales: Angular, RxJS, TypeScript, FastAPI, Pydantic, SQLAlchemy, psycopg, Alembic, Uvicorn, HTTPX, defusedxml, email-validator, python-multipart y pypdf. Infraestructura: Python, Node.js, nginx, PostgreSQL y pgvector. Herramientas de pruebas: pytest, HTTPX, Ruff y Vitest.

Antes de una distribución externa se debe completar el inventario legal de dependencias transitivas y de las imágenes utilizadas. Este listado inicial no sustituye sus textos de licencia ni afirma que todas tengan la misma licencia.

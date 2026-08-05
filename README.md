# Account App Backend

Backend de la aplicación de contabilidad construido con FastAPI y SQLAlchemy.

## Requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

## Instalación

```bash
uv sync
```

## Configuración

Crea un archivo `.env` con las siguientes variables:

```env
DATABASE_URL=sqlite:///./accountapp.db
JWT_SECRET_KEY=tu-clave-secreta
```

## Migraciones

```bash
uv run alembic upgrade head
```

## Ejecutar

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Documentación

Una vez en ejecución, la documentación interactiva está disponible en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tests

```bash
uv run pytest
```

## Licencia

MIT

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
COPY scripts ./scripts

RUN pip install --upgrade pip && pip install .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Use a non-root user
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install only production deps
COPY pyproject.toml poetry.local ./
RUN poetry install --no-dev

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

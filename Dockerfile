FROM python:3.9 as build_base

COPY pyproject.toml /app/
COPY README.md /app/
COPY . /app/backend_api/
RUN pip install --upgrade pip && \
    pip install poetry

FROM build_base as main_part
WORKDIR /app
RUN poetry export -f requirements.txt --output requirements.txt
RUN python -m pip install -r requirements.txt
WORKDIR /app/backend_api/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]

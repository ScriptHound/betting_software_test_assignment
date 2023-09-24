FROM python:3.9

COPY ./app /app

RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN python -m pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

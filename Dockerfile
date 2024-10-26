FROM python:3.10-slim

#RUN pip install --upgrade pip
RUN pip install poetry

RUN apt-get update && \
    apt-get install -y libpq-dev build-essential gcc && \
    apt-get clean

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app

CMD ["python", "main.py"]

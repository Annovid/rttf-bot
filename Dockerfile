FROM python:3.10-slim

RUN pip install poetry

RUN apt-get update && \
    apt-get install -y libpq-dev build-essential gcc && \
    apt-get clean

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

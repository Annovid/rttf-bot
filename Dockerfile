FROM python:3.10-slim

# Set timezone
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install poetry

RUN apt-get update && \
    apt-get install -y libpq-dev build-essential gcc cron && \
    apt-get clean

WORKDIR /app/src

COPY pyproject.toml poetry.lock* README.md /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab && crontab /etc/cron.d/crontab

CMD ["/app/entrypoint.sh"]

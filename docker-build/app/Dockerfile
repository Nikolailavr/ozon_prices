FROM python:3.13.3-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==2.1" setuptools

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY /src .

RUN chmod +x prestart.sh
RUN chmod +x run

ENTRYPOINT ["./prestart.sh"]
CMD ["./run"]
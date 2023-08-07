FROM python:3.11 AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONIOENCODING=utf-8 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

WORKDIR /app

RUN pip install "poetry>=1.5"

COPY poetry.lock pyproject.toml ./

FROM base AS dev

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


FROM base AS stage

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-dev --no-ansi

COPY . .

FROM base AS lint

COPY . /app

RUN pip install ruff

CMD ["ruff", "check", "."]

# Default ARG values for the stages.
ARG WORK_DIR=synth-features \
    API_PORT=8000

# The builder image, used to build the virtual environment
FROM python:3.11.11-alpine3.21 AS builder

ARG WORK_DIR

ENV TZ=Asia/Tokyo \
    VIRTUAL_ENV=/${WORK_DIR}/.venv \
    PATH="/${WORK_DIR}/.venv/bin:${PATH}"

RUN apk add --no-cache \
    gcc=14.2.0-r4 \
    musl-dev=1.2.5-r9 \
    python3-dev=3.12.11-r0 \
    libffi-dev=3.4.7-r0 \
    rust=1.83.0-r0 \
    cargo=1.83.0-r0 \
    libpq-dev=17.5-r0 \
    curl=8.12.1-r1

RUN pip install --no-cache-dir poetry==1.8.5

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /${WORK_DIR}


COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root \
    && rm -rf ${POETRY_CACHE_DIR}

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11.11-alpine3.21 AS runtime

ARG WORK_DIR API_PORT

ENV TZ=Asia/Tokyo \
    VIRTUAL_ENV=/${WORK_DIR}/.venv \
    PATH="/${WORK_DIR}/.venv/bin:${PATH}"

RUN apk add --no-cache \
    libgcc=14.2.0-r4 \
    curl=8.12.1-r1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Create a non-root user and group
RUN addgroup --system music_tech_group \
    && adduser --system --ingroup music_tech_group --home /${WORK_DIR} music_tech_user

RUN chown music_tech_user:music_tech_group /${WORK_DIR}

# Switch to the non-root user
USER music_tech_user

# Copy the rest of the application code into the container

COPY . /${WORK_DIR}

WORKDIR /${WORK_DIR}

# Expose the port your FastAPI app listens on
EXPOSE ${API_PORT}

ENV PYTHONPATH="/${WORK_DIR}/src" \
    API_PORT=${API_PORT} \
    ENV=${ENV}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:${API_PORT}/health/

ENTRYPOINT ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT}"]

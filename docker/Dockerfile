# Default ARG values for the stages.
ARG WORK_DIR=synth-features \
    API_PORT=8000

# Python base image version needs to lie in the python version
# decided by dependency manager (poetry).
# [AI Setback]: Runtime execution of Docker build

# The builder image, used to build the virtual environment
FROM python:3.11-slim AS builder

ARG WORK_DIR

ENV TZ=Asia/Tokyo \
    VIRTUAL_ENV=/${WORK_DIR}/.venv \
    PATH="/${WORK_DIR}/.venv/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    python3-dev \
    libffi-dev \
    libpq-dev \
    curl \
    pkg-config \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==2.1.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /${WORK_DIR}


COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root \
    && rm -rf ${POETRY_CACHE_DIR}

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim AS runtime

ARG WORK_DIR API_PORT

ENV TZ=Asia/Tokyo \
    VIRTUAL_ENV=/${WORK_DIR}/.venv \
    PATH="/${WORK_DIR}/.venv/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libasound2 \
    libportaudio2 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

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

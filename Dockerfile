# Stage 1 Build requirements
FROM python:3.12-alpine3.20 AS BUILDER

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    openjpeg-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2 Pod runtime
FROM python:3.12-alpine3.20

WORKDIR /app

RUN apk add --no-cache \
    libpq \
    tzdata \
    curl \
    libjpeg-turbo \
    zlib \
    openjpeg

# Injecting compiled dependencies from Stage 1 builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy entire project/codebase
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Standard sync worker deployment command for Gunicorn web pods
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]

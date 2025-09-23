# Multi-stage build for SkillForge Project Service
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/backend/project-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download Cloud SQL Proxy
RUN wget -O /usr/local/bin/cloud-sql-proxy \
    https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.7.0/cloud-sql-proxy.linux.amd64 \
    && chmod +x /usr/local/bin/cloud-sql-proxy

# Create non-root user for security
RUN groupadd -r skillforge && useradd -r -g skillforge skillforge && \
    mkdir -p /app && \
    chown -R skillforge:skillforge /app

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=skillforge:skillforge /root/.local /home/skillforge/.local

# Copy application code
COPY --chown=skillforge:skillforge apps/backend/project-service/app ./app
COPY --chown=skillforge:skillforge apps/backend/project-service/alembic ./alembic
COPY --chown=skillforge:skillforge apps/backend/project-service/alembic.ini ./alembic.ini
COPY --chown=skillforge:skillforge apps/backend/project-service/requirements.txt ./requirements.txt

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start Cloud SQL Proxy if connection string is provided\n\
if [ -n "$INSTANCE_CONNECTION_NAME" ]; then\n\
    echo "Starting Cloud SQL Proxy..."\n\
    /usr/local/bin/cloud-sql-proxy \
        --private-ip \
        --port 5432 \
        "$INSTANCE_CONNECTION_NAME" &\n\
    sleep 5\n\
fi\n\
\n\
# Run migrations\n\
echo "Running database migrations..."\n\
alembic upgrade head || echo "Migration failed, continuing..."\n\
\n\
# Start the application\n\
echo "Starting Project Service..."\n\
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers ${WORKERS:-4} \
    --loop uvloop \
    --access-log \
    --log-level ${LOG_LEVEL:-info}\n\
' > /app/start.sh && chmod +x /app/start.sh

# Update PATH
ENV PATH=/home/skillforge/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PORT=8080 \
    SERVICE_NAME=project-service

# Create directory for GCS credentials if needed
RUN mkdir -p /app/credentials && \
    chown skillforge:skillforge /app/credentials

# Switch to non-root user
USER skillforge

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8080

# Start script for production
CMD ["/app/start.sh"]
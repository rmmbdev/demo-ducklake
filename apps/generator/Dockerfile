FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates

RUN mkdir -p /root/.duckdb/extensions/v1.3.0/linux_amd64 && \
    curl -o /root/.duckdb/extensions/v1.3.0/linux_amd64/postgres_scanner.duckdb_extension.gz \
    http://extensions.duckdb.org/v1.3.0/linux_amd64/postgres_scanner.duckdb_extension.gz && \
    gunzip /root/.duckdb/extensions/v1.3.0/linux_amd64/postgres_scanner.duckdb_extension.gz && \
    curl -o /root/.duckdb/extensions/v1.3.0/linux_amd64/httpfs.duckdb_extension.gz \
    http://extensions.duckdb.org/v1.3.0/linux_amd64/httpfs.duckdb_extension.gz && \
    gunzip /root/.duckdb/extensions/v1.3.0/linux_amd64/httpfs.duckdb_extension.gz && \
    curl -o /root/.duckdb/extensions/v1.3.0/linux_amd64/ducklake.duckdb_extension.gz \
    http://extensions.duckdb.org/v1.3.0/linux_amd64/ducklake.duckdb_extension.gz && \
    gunzip /root/.duckdb/extensions/v1.3.0/linux_amd64/ducklake.duckdb_extension.gz

COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

WORKDIR /app
ENV PYTHONPATH="/app"
ENV UV_PROJECT_ENVIRONMENT="/usr/local"

COPY pyproject.toml .
RUN uv sync

COPY /src /app

COPY entrypoint.sh /app
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

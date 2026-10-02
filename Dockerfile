FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.13-alpine
COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_CACHE=1 \
    PATH="/app/.venv/bin:$PATH" DB_PATH=/data/robots.db
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app.py model.py ip_tools.py ./
COPY templates ./templates
COPY static ./static

RUN adduser -D app && mkdir /data && chown app /data
USER app
VOLUME /data
EXPOSE 3464
CMD ["gunicorn", "-b", "0.0.0.0:3464", "app:app"]

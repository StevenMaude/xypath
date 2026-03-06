FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY xypath ./xypath
RUN uv sync --frozen --extra test

COPY . .

CMD ["uv", "run", "--frozen", "--extra", "test", "pytest"]

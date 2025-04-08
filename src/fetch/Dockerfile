# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy project files first
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e .

FROM python:3.12-slim-bookworm

WORKDIR /app

# Install dependencies directly in the final image
COPY pyproject.toml uv.lock ./
COPY . .

# Install the project and its dependencies
RUN pip install --no-cache-dir -e .

# Create a script to handle both modes
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
if [ "\$1" = "sse" ]; then
    # Verify uvicorn is installed
    if ! command -v uvicorn &> /dev/null; then
        echo "Error: uvicorn not found in PATH: \$PATH"
        echo "Contents of /usr/local/bin:"
        ls -la /usr/local/bin
        exit 1
    fi
    exec uvicorn mcp_server_fetch.sse_server_fixed:app --host 0.0.0.0 --port 3001
else
    exec mcp-server-fetch "\$@"
fi
EOF

RUN chmod +x /app/entrypoint.sh

# Expose port 3001 for SSE mode
EXPOSE 3001

# Use the entrypoint script to handle both modes
ENTRYPOINT ["/app/entrypoint.sh"]

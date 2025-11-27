# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ ./secops_mcp/

# Install dependencies
# We use --system to install into the system python, which is fine in a container
RUN uv pip install --system .

# Expose the port
ENV PORT=8080
EXPOSE 8080

# Run the server using uvicorn
# We use the FastMCP ASGI app exposed by the server instance
# Note: We need to make sure server.py exposes the 'server' object which is the FastMCP instance
CMD ["uvicorn", "secops_mcp.server:server", "--host", "0.0.0.0", "--port", "8080"]


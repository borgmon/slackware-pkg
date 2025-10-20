FROM ghcr.io/astral-sh/uv:debian-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    tar \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (required for building ripgrep and other Rust packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files for dependency installation
COPY pyproject.toml uv.lock* ./

# Copy the entire project
COPY . .

# Install Python dependencies using uv
RUN uv sync --frozen

# Install the package in editable mode for development
RUN uv pip install -e .

# Set the virtual environment in PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Default command - run the package builder
CMD ["slackware-pkg"]

# For development/debugging, you can override with:
# docker run -it --entrypoint bash <image>

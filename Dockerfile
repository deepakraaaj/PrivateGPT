# Stage 1: Builder
# Use Python 3.10 slim as base (supports pre-built wheels for llama-cpp-python)
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies for compiling llama.cpp if no wheel is found
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies into a virtual environment to keep image clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install with valid pre-built wheel if possible, or build from source
# CMAKE_ARGS="-DGGML_NATIVE=ON" ensures optimizations for the host CPU (AVX/AVX2)
# For generic cloud deployment, we might remove `-DGGML_NATIVE=ON`, but for
# performance it is critical.
RUN CMAKE_ARGS="-DGGML_NATIVE=OFF" pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install runtime libs (libgomp for openmp support)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY main.py .
# Create models directory
RUN mkdir models

# Expose port
EXPOSE 8001

# Run server
# Workers=1 because LLM inference is CPU bound and single process per model is standard
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

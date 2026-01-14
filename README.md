# FastQwenRunner

A production-ready, high-performance API runner for the **Qwen 2.5 0.5B** LLM, built with `llama-cpp-python` and FastAPI.

Optimized for:
- 🚀 **Speed**: Uses quantized models (Q8_0) and multi-threaded CPU inference.
- 📉 **Cost**: Runs efficiently on standard CPUs (no GPU required).
- 🔌 **Standard**: OpenAI-compatible API (`/v1/chat/completions`).

## Prerequisites
- **Python 3.10** (Required for pre-built wheels)
- **Git**

## Quick Start (Linux/Mac)

1.  **Clone & Enter**
    ```bash
    git clone https://github.com/deepakraaaj/PrivateGPT.git
    cd PrivateGPT
    ```

2.  **Run the Start Script**
    This script handles everything: creates virtualenv, installs dependencies, downloads the model, and starts the server.
    ```bash
    chmod +x start.sh
    ./start.sh
    ```

3.  **Done!**
    The server is running at: `http://localhost:8001`

    - **Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)
    - **API Endpoint**: `http://localhost:8001/v1/chat/completions`

## Manual Setup

If you prefer to run it manually without `start.sh`:

```bash
# 1. Create Venv
python3.10 -m venv venv
source venv/bin/activate

# 2. Install Deps
pip install -r requirements.txt

# 3. Run Server
python main.py
```

## Docker Deployment

To run in a container (ideal for servers):

```bash
# Build
docker build -t fast-qwen-runner .

# Run (Port 8001)
docker run -d -p 8001:8001 --name qwen-runner fast-qwen-runner
```

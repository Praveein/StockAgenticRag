#!/bin/bash
# Quick Start Script for Stocks AI Agent with Local Ollama LLM

echo "======================================"
echo "Stocks AI Agent - Quick Start Setup"
echo "======================================"

# Step 1: Check if Ollama is installed
echo ""
echo "[1] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
else
    echo "✗ Ollama not found. Please install from https://ollama.ai"
    exit 1
fi

# Step 2: Check if Ollama server is running
echo ""
echo "[2] Checking if Ollama server is running..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama server is running"
else
    echo "✗ Ollama server is not running"
    echo "  Start it with: ollama serve"
    exit 1
fi

# Step 3: Check if models are available
echo ""
echo "[3] Checking for required models..."

# Check for qwen2.5-coder model
if ollama list | grep -q "qwen2.5-coder"; then
    echo "✓ Qwen2.5-Coder model found"
else
    echo "! Qwen2.5-Coder model not found"
    echo "  Installing Qwen2.5-Coder 7B..."
    ollama pull qwen2.5-coder:7b
fi

# Check for embedding model
if ollama list | grep -q "nomic-embed-text"; then
    echo "✓ Embedding model (nomic-embed-text) found"
else
    echo "! Embedding model not found"
    echo "  Installing nomic-embed-text..."
    ollama pull nomic-embed-text
fi

# Step 4: Install Python dependencies
echo ""
echo "[4] Installing Python dependencies..."
pip install -r requirements.txt

# Step 5: Configuration check
echo ""
echo "[5] Configuration check..."
if [ -f .env ]; then
    echo "✓ .env file exists"
    echo "  Ollama Base URL: $(grep OLLAMA_BASE_URL .env)"
    echo "  LLM Model: $(grep LLM_MODEL .env)"
else
    echo "! .env file not found"
fi

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  cd rest_api"
echo "  python -m uvicorn main:app --reload"
echo ""
echo "Then access the API at: http://localhost:8000"
echo ""
echo "For detailed setup instructions, see LOCAL_LLM_SETUP.md"

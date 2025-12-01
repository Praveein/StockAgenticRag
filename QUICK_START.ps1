# Quick Start Script for Stocks AI Agent with Local Ollama LLM (Windows PowerShell)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Stocks AI Agent - Quick Start Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Check if Ollama is installed
Write-Host ""
Write-Host "[1] Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version
    Write-Host "✓ Ollama is installed: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    exit 1
}

# Step 2: Check if Ollama server is running
Write-Host ""
Write-Host "[2] Checking if Ollama server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Ollama server is running" -ForegroundColor Green
    } else {
        throw "Connection failed"
    }
} catch {
    Write-Host "✗ Ollama server is not running" -ForegroundColor Red
    Write-Host "  Start it with: ollama serve" -ForegroundColor Yellow
    exit 1
}

# Step 3: Check if models are available
Write-Host ""
Write-Host "[3] Checking for required models..." -ForegroundColor Yellow

# Check for qwen2.5-coder model
$gemmaCheck = ollama list | Select-String "qwen2.5-coder"
if ($gemmaCheck) {
    Write-Host "✓ Qwen2.5-Coder model found" -ForegroundColor Green
} else {
    Write-Host "! Qwen2.5-Coder model not found" -ForegroundColor Yellow
    Write-Host "  Installing Qwen2.5-Coder 7B..." -ForegroundColor Yellow
    ollama pull qwen2.5-coder:7b
}

# Check for embedding model
$embeddingCheck = ollama list | Select-String "nomic-embed-text"
if ($embeddingCheck) {
    Write-Host "✓ Embedding model (nomic-embed-text) found" -ForegroundColor Green
} else {
    Write-Host "! Embedding model not found" -ForegroundColor Yellow
    Write-Host "  Installing nomic-embed-text..." -ForegroundColor Yellow
    ollama pull nomic-embed-text
}

# Step 4: Install Python dependencies
Write-Host ""
Write-Host "[4] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 5: Configuration check
Write-Host ""
Write-Host "[5] Configuration check..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
    $ollamaUrl = Select-String -Path ".env" -Pattern "OLLAMA_BASE_URL"
    $llmModel = Select-String -Path ".env" -Pattern "LLM_MODEL"
    Write-Host "  $ollamaUrl" -ForegroundColor Gray
    Write-Host "  $llmModel" -ForegroundColor Gray
} else {
    Write-Host "! .env file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  cd rest_api" -ForegroundColor White
Write-Host "  python -m uvicorn main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Then access the API at: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "For detailed setup instructions, see LOCAL_LLM_SETUP.md" -ForegroundColor Yellow

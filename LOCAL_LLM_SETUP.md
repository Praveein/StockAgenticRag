# Local LLM Setup Guide

This project has been configured to use **Ollama** with **Gemma 2B** (or Gemma 7B) as a local LLM, replacing the OpenAI API dependency.

## Prerequisites

### 1. Install Ollama
- **Download**: https://ollama.ai
- **Installation**: Follow the installation instructions for your OS (Windows, macOS, Linux)
- **Verify Installation**: Run `ollama --version` in terminal

### 2. Pull Gemma Model

After installing Ollama, pull the Gemma model:

```bash
# For Gemma 2B (faster, lighter)
ollama pull gemma:2b

# OR for Gemma 7B (more capable, requires more resources)
ollama pull gemma:7b
```

### 3. Pull Embedding Model

```bash
ollama pull nomic-embed-text
```

### 4. Start Ollama Server

```bash
# On Windows: Ollama typically runs as a background service
# On macOS/Linux:
ollama serve
```

The server will run on `http://localhost:11434` by default.

## Configuration

The project is pre-configured with the following environment variables in `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=gemma:2b
EMBEDDING_MODEL=nomic-embed-text
```

### To Use Gemma 7B Instead:

Edit `.env` and change:
```env
LLM_MODEL=gemma:7b
```

### Optional: Configure Tavily Search

If you have a Tavily API key for web search:

```env
TAVILY_API_KEY=your_tavily_api_key
```

If not provided, the system will use mock search results.

## Project Changes

### Files Modified:

1. **config/llm_config.py** (NEW)
   - Central configuration for Ollama LLM and embeddings
   - Provides singleton instances for efficient resource usage

2. **Chain Files Updated**:
   - `rag_graphs/news_rag_graph/graph/chains/generation.py`
   - `rag_graphs/news_rag_graph/graph/chains/retrieval_grader.py`
   - `rag_graphs/stock_data_rag_graph/graph/chains/sql_generation_chain.py`
   - `rag_graphs/stock_data_rag_graph/graph/chains/retrieval_grader.py`
   - `rag_graphs/stock_data_rag_graph/graph/chains/results_generation.py`

3. **Embeddings Configuration**:
   - `rag_graphs/news_rag_graph/ingestion.py` - Now uses local embeddings

4. **Web Search**:
   - `rag_graphs/news_rag_graph/graph/nodes/web_search.py` - Gracefully falls back to mock search if Tavily unavailable

5. **Dependencies**:
   - `requirements.txt` - Removed `langchain-openai`, kept other dependencies

6. **Environment**:
   - `.env` - Updated with Ollama configuration
   - `conftest.py` - Updated for testing with local LLM

## Running the Application

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Services are Running

- **Ollama Server**: Running on `http://localhost:11434`
- **PostgreSQL**: Running on configured host/port (if using stock data features)
- **MongoDB**: Running (if using news scraper features)

### 3. Run the FastAPI Application

```bash
cd rest_api
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# News endpoint
curl http://localhost:8000/news/AAPL?topic=AI

# Stock endpoint
curl http://localhost:8000/stock/AAPL/price-stats

# Chart endpoint
curl http://localhost:8000/stock/AAPL/chart?price_type=close&duration=7
```

## Performance Considerations

### Gemma 2B
- **Pros**: Lightweight, fast, requires ~2GB RAM
- **Cons**: Less accurate than larger models
- **Best for**: Quick prototyping, limited hardware

### Gemma 7B
- **Pros**: Better accuracy, more capable
- **Cons**: Slower, requires ~7GB RAM
- **Best for**: Production use, better quality needed

## Troubleshooting

### Issue: "Connection refused" when connecting to Ollama

**Solution**: 
```bash
# Make sure Ollama is running
ollama serve
```

### Issue: Model not found

**Solution**: 
```bash
# Pull the model again
ollama pull gemma:2b
ollama pull nomic-embed-text
```

### Issue: Out of memory

**Solution**:
- Use `gemma:2b` instead of `gemma:7b`
- Close other applications
- Reduce batch sizes in application configuration

### Issue: Slow responses

**Reason**: LLM inference is slower than cloud APIs
- First response might be slower while model loads
- Gemma 7B will be slower than 2B
- This is expected behavior with local inference

## Advanced Configuration

### Custom Model

To use a different model supported by Ollama:

1. Pull the model: `ollama pull <model-name>`
2. Update `.env`: `LLM_MODEL=<model-name>`

### Different Base URL

If Ollama runs on a different machine:

```env
OLLAMA_BASE_URL=http://other-machine-ip:11434
```

## API Keys Removed

The following API keys are **no longer needed**:
- ❌ OpenAI API Key
- ❌ (Optional) Tavily API Key (system works without it)

## Next Steps

1. Start Ollama server
2. Pull models
3. Install Python dependencies
4. Run the application
5. Test the endpoints

For more details on using the application, refer to the main `README.md`

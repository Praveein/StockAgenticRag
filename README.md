# Stock Data Insights Application (Local LLM Edition)

This project demonstrates the use of **Agentic Retrieval-Augmented Generation (RAG)** workflows to extract insights from news and financial data using **100% Local LLMs**. It leverages **Ollama**, **LangChain**, **LangGraph**, and **ChromaDB** to provide comprehensive analyses without relying on external APIs like OpenAI.

## 🌟 Features

- **Local LLM Inference**: Uses qwen2.5-coder:7b via Ollama for all reasoning and generation tasks.
- **Interactive UI**: A user-friendly **Streamlit** dashboard for visualizing stock data and news.
- **Stock Performance Visualization**: Interactive charts using **Altair** to visualize historical stock performance.
- **Attribute-Specific Data Retrieval**: Fetches detailed financial stats (e.g., average close price) using SQL generation.
- **News Aggregation**: Scrapes and analyzes news articles using a local RAG pipeline with **MongoDB** and **ChromaDB**.
- **Privacy-First**: All data processing and LLM inference happen locally on your machine.

## 🏗️ High Level Architecture

![High Level Design](documentation/high_level_design.png)

The system consists of:
1.  **Frontend**: Streamlit UI for user interaction.
2.  **Backend**: FastAPI server handling API requests.
3.  **LLM Engine**: Ollama running qwen2.5-coder:7b and 
omic-embed-text.
4.  **Databases**:
    *   **PostgreSQL**: Stores structured stock price data.
    *   **MongoDB**: Stores raw news articles.
    *   **ChromaDB**: Stores vector embeddings for semantic search.

## 🚀 Setup & Installation

### 1. Prerequisites
*   **Python 3.10+**
*   **Ollama**: [Download here](https://ollama.ai)
*   **PostgreSQL** (running locally)
*   **MongoDB** (running locally)

### 2. Install Ollama Models
Open a terminal and run:
`ash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
ollama serve
`

### 3. Install Dependencies
`ash
pip install -r requirements.txt
`

### 4. Configure Environment
Create a .env file in the stocks-insights-ai-agent directory:
`nv
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5-coder:7b
EMBEDDING_MODEL=nomic-embed-text
POSTGRES_HOST=localhost
POSTGRES_DB=stock_data_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
MONGO_URI=mongodb://localhost:27017/
`

## 🏃‍♂️ Running the Application

You need to run both the backend and frontend in separate terminals.

**Terminal 1: Backend API**
`ash
cd stocks-insights-ai-agent
python -m uvicorn rest_api.main:app --reload
`
*API will be available at http://localhost:8000*

**Terminal 2: Streamlit UI**
`ash
cd stocks-insights-ai-agent
streamlit run streamlit_app.py
`
*UI will open at http://localhost:8501*

## 🧠 RAG Workflows

### News Data RAG
*   **Retrieval**: Searches ChromaDB for relevant news chunks.
*   **Grading**: LLM evaluates if retrieved documents are relevant.
*   **Generation**: LLM answers the user query based on the context.

### Stock Data RAG (SQL)
*   **SQL Generation**: LLM converts natural language questions (e.g., verage close price of TCS last week) into SQL queries.
*   **Execution**: Runs the query against PostgreSQL.
*   **Response**: LLM interprets the SQL result and provides a natural language answer.

## 📡 API Endpoints

### Stock Data
*   GET /stock/{ticker}/price-stats: Get statistical data (average, high, low).
*   GET /stock/{ticker}/chart: Get chart data (JSON series or PNG).

### News
*   GET /news/{ticker}: Get summarized news insights for a stock.

## 🛠️ Tech Stack
*   **LLM**: Ollama (qwen2.5-coder:7b)
*   **Embeddings**: 
omic-embed-text
*   **Orchestration**: LangChain, LangGraph
*   **Backend**: FastAPI
*   **Frontend**: Streamlit, Altair
*   **Database**: PostgreSQL, MongoDB, ChromaDB

## 📝 License
This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).

---
*Last Updated: 2025-12-01*

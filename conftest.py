import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Using local Ollama instead of OpenAI, no API key needed
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

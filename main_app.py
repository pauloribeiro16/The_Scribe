# main_app.py

import logging
import sys
import beaupy
import requests

from core.RAGEngine import RAGEngine
# --- NEW: Import the DSS Session Manager ---
from core.DSS_Session import DSS_Session

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank

# ... (logging and model configuration remain the same) ...
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL_NAME = "nomic-embed-text"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"
RERANKER_TOP_N = 5

def list_ollama_models(exclude_prefix="nomic"):
    # ... (this function remains the same) ...
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        models = [m["name"] for m in response.json().get("models", [])]
        return sorted([m for m in models if not m.startswith(exclude_prefix)])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error contacting Ollama at {OLLAMA_BASE_URL}. Is it running? Details: {e}")
        return []

def select_and_initialize_models():
    # ... (this function remains the same) ...
    logging.info("Initializing AI models...")
    available_models = list_ollama_models()
    if not available_models:
        logging.error("No compatible Ollama models found. Exiting."); sys.exit(1)
    print("\nPlease select the main LLM you want to use for response synthesis:")
    selected_llm_name = beaupy.select(available_models, cursor=">", cursor_style="green")
    if not selected_llm_name:
        print("No model selected. Exiting."); sys.exit(1)
    try:
        embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL_NAME, base_url=OLLAMA_BASE_URL)
        llm = Ollama(model=selected_llm_name, base_url=OLLAMA_BASE_URL, request_timeout=800,context_window=10096)
        reranker = SentenceTransformerRerank(model=RERANKER_MODEL, top_n=RERANKER_TOP_N)
        logging.info(f"Models initialized successfully. Using LLM: {selected_llm_name}")
        return embed_model, llm, reranker
    except Exception as e:
        logging.error(f"Failed to initialize models. Error: {e}"); sys.exit(1)


def main():
    print("--- AI-Powered Cybersecurity Decision Support System ---")
    
    embed_model, llm, reranker = select_and_initialize_models()

    # The RAG Engine is a tool that the DSS will use.
    rag_engine = RAGEngine(
        embed_model=embed_model,
        llm=llm,
        reranker=reranker
    )

    while True:
        print("\n" + "="*25 + " MAIN MENU " + "="*25)
        main_menu_options = [
            "1. Launch The Scribe",
            "2. Use the Direct RAG Researcher",
            "3. Exit"
        ]
        selection = beaupy.select(main_menu_options, cursor=">", cursor_style="green")
        
        if not selection or "Exit" in selection:
            print("Goodbye!"); break

        if "The Scribe" in selection:
            # --- Launch the new, interactive DSS session ---
            dss_session = DSS_Session(llm, rag_engine)
            dss_session.start_session()
            
        elif "Direct RAG Researcher" in selection:
            # --- This is our previous, direct query mode ---
            question = beaupy.prompt("\nEnter your research question:")
            if question:
                print("\nResearching... (this may take a moment)")
                result = rag_engine.query(question)
                
                print("\n" + "="*20 + " RESPONSE " + "="*20)
                print(result['response'])
                print(f"\n(Query completed in {result['duration']:.2f} seconds)")
                print("="*50)

if __name__ == "__main__":
    main()
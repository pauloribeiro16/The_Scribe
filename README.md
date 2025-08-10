# The Scribe: An AI Co-Pilot for Secure Software Requirements

**The Scribe is an AI-powered Decision Support System (DSS) designed to guide software practitioners through the complex process of defining secure and privacy-respecting software requirements.**

Developed as a core component of a Master's thesis on decision support for security requirements, The Scribe acts as an intelligent co-pilot. It embeds the **SPIDESOFT methodology**—a structured, two-phased approach to integrating security from the earliest stages of the software development lifecycle (SDLC).

Unlike traditional tools that act as passive checklists or simple search engines, The Scribe engages the user in a collaborative, Socratic dialogue. It helps analysts and developers think critically about security, identify unspoken risks, and produce a comprehensive, traceable, and compliant **Security & Privacy Requirements Specification (S&PRS)** document.

---

## The Core Problem The Scribe Solves

In modern software development, security is often treated as an afterthought. High-level strategic goals (e.g., "the system must be secure") frequently fail to translate into actionable, verifiable requirements for development teams. This gap leads to vulnerabilities, compliance issues, and costly rework.

The Scribe addresses this by:
1.  **Enforcing a Systematic Process:** It provides a structured workflow based on the SPIDESOFT method, ensuring no critical step is missed.
2.  **Augmenting Human Intelligence:** It uses an AI co-pilot to ask critical questions, analyze user input, and highlight potential risks the user may not have considered.
3.  **Ensuring Traceability & Compliance:** Every requirement generated is explicitly linked back to its business, legal, and risk drivers, creating an auditable trail that is essential for regulations like GDPR.

## Key Features & Architecture

The Scribe is built on a sophisticated, multi-layered AI architecture designed for both precision and deep contextual understanding.

-   **Interactive DSS Co-Pilot:** The primary interface is a conversational agent that guides the user through the SPIDESOFT methodology, from defining the project's purpose to threat modeling and control identification.
-   **Advanced RAG Engine:** At its core, The Scribe utilizes a powerful Retrieval-Augmented Generation (RAG) engine with a rich knowledge base, including:
    -   **Threat Intelligence:** CWE, CAPEC, D3FEND
    -   **Frameworks & Standards:** NIST SP 800-53, NIST CSF, ISO 27002
    -   **Regulations:** GDPR, DORA, NIS2
-   **Intelligent Multi-Document Router:** An LLM-powered router analyzes the user's query and the current context to select the most relevant knowledge base(s) to search, enabling powerful cross-domain synthesis (e.g., linking a CWE weakness to a NIST control).
-   **Hybrid Retrieval System:** The engine combines multiple retrieval strategies to ensure the best possible context is found:
    -   **Metadata Filtering:** For precise, keyword-based lookups of specific IDs (e.g., `CWE-79`).
    -   **Semantic Search with Query Expansion:** For broad, conceptual questions, the engine expands the user's query with related technical terms to find relevant information even when keywords don't match.
-   **Per-Source Reranking:** To ensure context from all relevant sources is presented, a cross-encoder reranks the retrieved results for each knowledge base independently before fusing them into the final context for the LLM.

## Getting Started

### Prerequisites

*   Python 3.10+
*   An Ollama instance running locally. You can download it from [ollama.com](https://ollama.com/).
*   The required Ollama models. At a minimum, you will need:
    -   A small model for routing (e.g., `qwen2:0.5b` or `phi3`): `ollama pull qwen2:0.5b`
    -   An embedding model: `ollama pull nomic-embed-text`
    -   A primary LLM for synthesis (e.g., `gemma2:9b` or `llama3`): `ollama pull gemma2:9b`
*   The document sources (XML, TTL, TXT files) placed in the `/docs` directory.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[TODO: Your-GitHub-Username]/TheScribe.git
    cd TheScribe
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Ensure your Ollama server is running.**
2.  **Run the main application:**
    ```bash
    python main_app.py
    ```3.  The application will start, and you will be prompted to select an LLM and then choose a mode from the main menu. It is highly recommended to start with the **SPIDESOFT DSS Co-Pilot**.

## Project Status

This project is currently under active development. The core RAG engine and the DSS Co-Pilot for SPIDESOFT Phase 1 are implemented and functional. Future work will focus on:
*   Implementing the interactive guide for SPIDESOFT Phase 2 (Elaboration and Secure Design).
*   Integrating a Knowledge Graph to enhance the understanding of relationships between entities.
*   Developing specialized "expert" agents for tasks like automated threat modeling.
*   Creating a module to automatically generate the final, formatted S&PRS document.

## Acknowledgements

This project was developed in the context of a PhD's Thesis at `Minho University`. The core methodology, SPIDESOFT, is an original contribution aimed at improving the state of the art in secure software engineering.

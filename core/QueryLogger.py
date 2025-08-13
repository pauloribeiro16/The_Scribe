# core/QueryLogger.py

import logging
import os
import json
from datetime import datetime

class QueryLogger:
    """
    A dedicated logger that records the entire, detailed flow of a single RAG query,
    including all internal LLM calls, into a structured log file.
    """
    def __init__(self, dss_logger_instance=None, log_directory="query_logs"):
        if dss_logger_instance:
            # If we are given an existing DSS logger, just use it.
            self.logger = dss_logger_instance
        else:
            # Otherwise, create a new file-based logger for standalone RAG queries.
            os.makedirs(log_directory, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self.log_filepath = os.path.join(log_directory, f"query_log_{timestamp}.log")
            
            self.logger = logging.getLogger(f"QueryLogger_{timestamp}")
        self.logger.setLevel(logging.INFO)
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        handler = logging.FileHandler(self.log_filepath, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def _log_separator(self, title):
        self.logger.info("\n" + "="*25 + f" {title.upper()} " + "="*25)

    def log_start(self, user_query):
        self._log_separator("START OF QUERY")
        self.logger.info(f"User Query: {user_query}")

    # --- NEW: DETAILED LOGGING FOR INTERNAL LLM STEPS ---
    def log_llm_step(self, step_name: str, prompt: str, raw_response: str, parsed_result: any):
        """Logs the complete details of an internal LLM call (like router or expander)."""
        self._log_separator(f"RAG STEP: {step_name}")
        self.logger.info(f"--- PROMPT SENT TO PLANNER LLM ---\n{prompt}\n")
        self.logger.info(f"--- RAW RESPONSE FROM PLANNER LLM ---\n{raw_response}\n")
        self.logger.info(f"--- PARSED RESULT ---\n{json.dumps(parsed_result, indent=2)}")
    # --- END NEW ---

    def log_plan(self, plan: dict):
        self._log_separator("MASTER RETRIEVAL PLAN")
        self.logger.info(json.dumps(plan, indent=2))

    def log_retrieved_nodes(self, nodes, source: str):
        self.logger.info(f"\n--- Retrieved Nodes (Chunks) from '{source}' ---")
        if not nodes:
            self.logger.info("No nodes were retrieved.")
            return
        for i, node in enumerate(nodes):
            score = node.get_score()
            score_str = f"{score:.4f}" if score else "N/A"
            self.logger.info(f"\n[Node {i+1} | Score: {score_str}] - Content: {node.get_content().strip()}")
        self.logger.info("-" * 60)

    def log_reranked_nodes(self, nodes, original_query: str):
        self._log_separator(f"RE-RANKED NODES")
        if not nodes:
            self.logger.info("No nodes were re-ranked.")
            return
        for i, node in enumerate(nodes):
            score_str = f"{node.score:.4f}" if hasattr(node, 'score') else "N/A"
            self.logger.info(f"\n[Re-Ranked Node {i+1} | Score: {score_str}] - Content: {node.node.get_content().strip()}")
        self.logger.info("-" * 60)

    def log_final_prompt(self, final_prompt: str):
        self._log_separator("FINAL PROMPT TO SYNTHESIS LLM")
        self.logger.info(final_prompt)

    def log_final_response(self, response: str, duration: float):
        self._log_separator("FINAL RESPONSE")
        self.logger.info(f"Response: {response}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self._log_separator("END OF QUERY")
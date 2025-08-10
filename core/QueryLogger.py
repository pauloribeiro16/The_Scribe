# core/query_logger.py

import logging
import os
import json
from datetime import datetime

class QueryLogger:
    """
    Uma classe de logger dedicada a registar todo o fluxo de uma única consulta RAG
    num ficheiro de log separado e estruturado.
    """
    def __init__(self, log_directory="query_logs"):
        # Cria o diretório de logs se não existir
        os.makedirs(log_directory, exist_ok=True)
        
        # Gera um nome de ficheiro único com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.log_filepath = os.path.join(log_directory, f"query_log_{timestamp}.log")
        
        # Configura o logger
        self.logger = logging.getLogger(f"QueryLogger_{timestamp}")
        self.logger.setLevel(logging.INFO)
        
        # Remove handlers existentes para evitar duplicação
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        # Cria um file handler e um formatter
        handler = logging.FileHandler(self.log_filepath, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False # Impede que os logs apareçam na consola

    def _log_separator(self, title):
        self.logger.info("\n" + "="*25 + f" {title.upper()} " + "="*25)

    def log_start(self, user_query):
        self._log_separator("START OF QUERY")
        self.logger.info(f"User Query: {user_query}")

    def log_plan(self, plan: dict):
        self._log_separator("DECOMPOSITION PLAN")
        self.logger.info(json.dumps(plan, indent=2))

    def log_error(self, message: str):
        self._log_separator("ERROR OCCURRED")
        self.logger.info(message)

    def log_sub_query_routing(self, sub_query: str, routed_to: str):
        self._log_separator(f"SUB-QUERY ROUTING: {sub_query[:50]}...")
        self.logger.info(f"Sub-Query: {sub_query}")
        self.logger.info(f"Routed To Document: {routed_to}")

    def log_retrieved_nodes(self, nodes, sub_query: str):
        self.logger.info(f"\n--- Retrieved Nodes (Chunks) for '{sub_query[:50]}...' ---")
        if not nodes:
            self.logger.info("No nodes were retrieved.")
            return
            
        for i, node in enumerate(nodes):
            score = node.get_score()
            score_str = f"{score:.4f}" if score else "N/A"
            self.logger.info(f"\n[Node {i+1} | Score: {score_str}]")
            self.logger.info(f"Content: {node.get_content().strip()}")
        self.logger.info("-" * 60)

    def log_reranked_nodes(self, nodes, original_query: str):
        self._log_separator(f"RE-RANKED NODES for Main Query: {original_query[:50]}...")
        if not nodes:
            self.logger.info("No nodes were re-ranked.")
            return

        for i, node in enumerate(nodes):
            score = node.score if hasattr(node, 'score') else "N/A"
            score_str = f"{score:.4f}" if isinstance(score, float) else str(score)
            
            # O reranker usa NodeWithScore, então o texto está em node.node
            content = node.node.get_content().strip()
            
            self.logger.info(f"\n[Re-Ranked Node {i+1} | Score: {score_str}]")
            self.logger.info(f"Content: {content}")
        self.logger.info("-" * 60)

    def log_final_prompt(self, final_prompt: str):
        self._log_separator("FINAL PROMPT TO LLM")
        self.logger.info(final_prompt)

    def log_final_response(self, response: str, duration: float):
        self._log_separator("FINAL RESPONSE")
        self.logger.info(f"Response: {response}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self._log_separator("END OF QUERY")
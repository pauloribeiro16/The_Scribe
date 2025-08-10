# core/RAGEngine.py (Final, Unified, and Corrected Implementation)

import logging
import time
import os
import re
import json
from typing import List, Dict, Any
from collections import defaultdict

from llama_index.core import VectorStoreIndex, StorageContext, QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.ollama import Ollama
from qdrant_client import QdrantClient

from config.knowledge_bases_config import ALL_KNOWLEDGE_BASES
from config.models_config import ROUTER_MODEL_NAME
from core.QueryLogger import QueryLogger

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QDRANT_PERSIST_PATH = os.path.join(SCRIPT_DIR, '..', "qdrant_storage_unified")
os.makedirs(QDRANT_PERSIST_PATH, exist_ok=True)

class RAGEngine:
    """
    An advanced RAG engine implementing a multi-stage, intelligent retrieval process:
    1.  A Unified Router selects the best knowledge base(s) from all available sources.
    2.  A Hybrid Planner creates steps for both keyword (metadata) and semantic search.
    3.  Query Expansion enriches semantic searches with related concepts.
    4.  Per-Source Reranking ensures balanced context from all selected sources.
    """
    def __init__(self, embed_model, llm, reranker):
        logging.info("Initializing RAG Engine with Hybrid-Fused Retrieval...")
        self.embed_model = embed_model
        self.llm = llm
        self.reranker = reranker
        
        self.planner_llm = Ollama(model=ROUTER_MODEL_NAME, base_url="http://localhost:11434", request_timeout=360.0, context_window=4096)
        self.qdrant_client = QdrantClient(path=QDRANT_PERSIST_PATH)
        
        self.knowledge_bases = ALL_KNOWLEDGE_BASES
        self._rag_component_cache = {}
        self.knowledge_base_descriptions = {name: config['description'] for name, config in self.knowledge_bases.items()}
        
        self.id_to_key_map = {
             "CWE": "cwe_id", "CAPEC": "capec_id", "AC": "control_id", "AT": "control_id", "AU": "control_id", "CA": "control_id", "CM": "control_id", "CP": "control_id", "IA": "control_id", "IR": "control_id", "MA": "control_id", "MP": "control_id", "PE": "control_id", "PL": "control_id", "PM": "control_id", "PS": "control_id", "PT": "control_id", "RA": "control_id", "SA": "control_id", "SC": "control_id", "SI": "control_id", "SR": "control_id", "GV": "subcategory_id", "ID": "subcategory_id", "PR": "subcategory_id", "DE": "subcategory_id", "RS": "subcategory_id", "RC": "subcategory_id",
        }
        logging.info("RAG Engine with Hybrid-Fused Retrieval is ready.")

    def _call_router_llm(self, prompt: str) -> List[str]:
        response_text = self.planner_llm.complete(prompt).text
        try:
            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if json_match: return json.loads(json_match.group(0))
        except (json.JSONDecodeError, TypeError):
            logging.warning(f"Router LLM failed to return a valid JSON list. Response: {response_text}")
        return []

    def _get_rag_component(self, kb_name: str):
        if kb_name not in self._rag_component_cache:
            logging.info(f"Initializing RAG component for '{kb_name}'...")
            config = self.knowledge_bases.get(kb_name)
            if not config:
                self._rag_component_cache[kb_name] = None
                return None
            self._rag_component_cache[kb_name] = self._RAGComponentInternal(config, self.embed_model, self.qdrant_client)
        return self._rag_component_cache.get(kb_name)

    def _initialize_all_components(self):
        for kb_name in self.knowledge_bases.keys(): self._get_rag_component(kb_name)

    # --- Step 1: Intelligent Source Selection ---
    def _select_knowledge_bases(self, user_query: str, logger: QueryLogger) -> List[str]:
        logging.info("Unified Router: Selecting best-fit knowledge base(s)...")
        selection_prompt = (
            "You are an expert query analyst. Your task is to select the most relevant document(s) from a list to answer a user's query.\n"
            "Analyze if the query requires information from multiple documents for comparison.\n\n"
            f"**Available Documents:**\n{json.dumps(self.knowledge_base_descriptions, indent=2)}\n\n"
            f"**User Query:** \"{user_query}\"\n\n"
            "**Instructions:**\n"
            "1. If the query asks to relate concepts from different documents (e.g., 'CWE' and 'NIST'), you **must** select both corresponding documents.\n"
            "2. If the user asks a general question, select only the single best document.\n\n"
            "Respond with only a JSON list of the selected document names. Example: `[\"CWE\", \"NIST SP 800-53 Rev. 5\"]`"
        )
        selected_docs = self._call_router_llm(selection_prompt)
        logger.log_plan({"step": "Source Selection", "result": selected_docs})
        return selected_docs

    # --- Step 2: Hybrid Plan Creation ---
    def _create_retrieval_plan(self, user_query: str, selected_kb_name: str) -> List[Dict[str, Any]]:
        id_pattern = re.compile(
            r'\b(CWE|CAPEC|AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|PT|RA|SA|SC|SI|SR|GV|ID|PR|DE|RS|RC)[-]([\d][\w().-]+)\b',
            re.IGNORECASE
        )
        found_ids = [match.group(0).upper().replace(' ', '-') for match in id_pattern.finditer(user_query)]
        plan = []
        if found_ids:
            for entity_id in found_ids:
                plan.append({"method": "metadata_filter", "value": entity_id, "kb_name": selected_kb_name})
        if not found_ids or len(user_query.split()) > 5:
            plan.append({"method": "semantic_search", "value": user_query, "kb_name": selected_kb_name})
        if not plan:
             plan.append({"method": "semantic_search", "value": user_query, "kb_name": selected_kb_name})
        return plan

    # --- Step 3: Query Expansion (for semantic steps) ---
    def _expand_query_for_semantic_search(self, user_query: str, logger: QueryLogger) -> List[str]:
        logging.info("Query Expansion: Generating related concepts...")
        expansion_prompt = (
            "You are a cybersecurity domain expert. Based on the user's query, generate a list of 5 related technical concepts or synonyms for a vector database search.\n\n"
            f"**User Query:** \"{user_query}\"\n\n"
            "**Example:**\n- Query: 'what are the best controls for ransomware?'\n- Response: `[\"data backup and recovery\", \"preventing unauthorized execution\", \"malware detection\", \"attack surface reduction\", \"incident response playbooks\"]`\n\n"
            "Respond with only a JSON list of strings."
        )
        expanded_terms = self._call_router_llm(expansion_prompt)
        final_search_terms = list(set([user_query] + expanded_terms))
        logger.log_plan({"step": "Query Expansion", "original_query": user_query, "expanded_terms": final_search_terms})
        return final_search_terms

    # --- Step 4: Plan Execution ---
    def _execute_retrieval_step(self, step: Dict[str, Any]) -> List[NodeWithScore]:
        kb_name = step["kb_name"]
        method = step["method"]
        value = step["value"]
        component = self._get_rag_component(kb_name)
        if not component or not component.index: return []

        if method == "metadata_filter":
            prefix = value.split('-')[0].split('.')[0]
            key_to_filter = self.id_to_key_map.get(prefix)
            if not key_to_filter: return []
            retriever = component.index.as_retriever(similarity_top_k=20, filters=MetadataFilters(filters=[ExactMatchFilter(key=key_to_filter, value=value)]))
            return retriever.retrieve(value)

        elif method == "semantic_search":
            search_terms = value if isinstance(value, list) else [value]
            retrieved_nodes = {}
            retriever = component.index.as_retriever(similarity_top_k=10)
            for term in search_terms:
                for node in retriever.retrieve(term):
                    retrieved_nodes[node.node.id_] = node
            return list(retrieved_nodes.values())
        return []

    # --- THE MAIN QUERY ORCHESTRATOR ---
    def query(self, user_query: str) -> dict:
        logger = QueryLogger()
        logger.log_start(user_query)
        start_time = time.perf_counter()
        self._initialize_all_components()

        # Step 1: Select KBs
        selected_kbs = self._select_knowledge_bases(user_query, logger)
        if not selected_kbs:
            return {"response": "I could not determine which documents to search.", "duration": time.perf_counter() - start_time, "context": ""}

        # Step 2: Create a master plan and expand semantic queries
        master_plan = []
        for kb_name in selected_kbs:
            plan_for_kb = self._create_retrieval_plan(user_query, kb_name)
            master_plan.extend(plan_for_kb)

        for step in master_plan:
            if step['method'] == 'semantic_search':
                expanded_terms = self._expand_query_for_semantic_search(user_query, logger)
                step['value'] = expanded_terms
        
        logger.log_plan({"step": "Master Plan Creation", "plan": master_plan})
        
        # Step 3: Execute the master plan
        initial_nodes: Dict[str, NodeWithScore] = {}
        for step in master_plan:
            nodes_from_step = self._execute_retrieval_step(step)
            for node in nodes_from_step:
                initial_nodes[node.node.id_] = node
        
        logger.log_retrieved_nodes(list(initial_nodes.values()), "Consolidated from all plan steps")

        if not initial_nodes:
            return {"response": f"I found the right documents ({', '.join(selected_kbs)}), but could not retrieve specific information.", "duration": time.perf_counter() - start_time, "context": ""}

        # Step 4: Per-Source Reranking
        nodes_by_source = defaultdict(list)
        for node in initial_nodes.values():
            nodes_by_source[node.node.metadata.get("source_document", "Unknown")].append(node)

        final_context_nodes = []
        for source, nodes in nodes_by_source.items():
            reranked_group = self.reranker.postprocess_nodes(nodes, query_bundle=QueryBundle(user_query))
            final_context_nodes.extend(reranked_group)
        
        logger.log_reranked_nodes(final_context_nodes, "Final combined after per-source reranking")
        final_context = "\n\n---\n\n".join([node.node.get_content() for node in final_context_nodes])

        # Step 5: Synthesize Final Answer
        system_prompt = (
            "You are a highly intelligent cybersecurity research analyst. Your primary task is to provide a comprehensive and accurate answer to the user's question, using the provided text excerpts as your primary source of truth.\n\n"
            "**Core Instructions:**\n"
            "1. **Prioritize the Context:** Your answer must be grounded in the facts and details found in the provided context.\n"
            "2. **Augment with Your Knowledge:** You are encouraged to use your own general knowledge to explain concepts and connect ideas, but your knowledge must not contradict the context.\n"
            "3. **Synthesize and Relate:** If the context provides information from multiple sources, your main task is to synthesize these pieces of information.\n"
            "4. **Address the User Directly:** Formulate the response as a direct, helpful answer to the user's question."
        )
        full_prompt = f"System: {system_prompt}\n\n--- Provided Context ---\n{final_context}\n--- End of Context ---\n\nQuestion: {user_query}\n\nAnswer:"
        logger.log_final_prompt(full_prompt)

        response = self.llm.complete(full_prompt)
        duration = time.perf_counter() - start_time
        
        return {"response": str(response).strip(), "duration": duration, "context": final_context}
    
    # The internal class for indexing remains the same.
    class _RAGComponentInternal:
        def __init__(self, config: dict, embed_model, qdrant_client: QdrantClient):
            self.config = config; self.embed_model = embed_model
            vector_store = QdrantVectorStore(client=qdrant_client, collection_name=config['collection_name'])
            try: collection_exists = qdrant_client.collection_exists(config['collection_name'])
            except Exception: collection_exists = False
            if not collection_exists:
                logging.info(f"Indexing '{config['name']}'...")
                parser = config['parser']
                documents = parser(config['file_path'])
                if not documents: self.index = None; return
                if config['name'] in ["D3FEND", "GDPR", "DORA", "NIS2 Directive", "NIST CSF 2.0", "ISO/IEC 27002:2022"]:
                    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
                else: 
                    node_parser = SentenceSplitter(chunk_size=8192, chunk_overlap=0)
                storage_context = StorageContext.from_defaults(vector_store=vector_store)
                self.index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=self.embed_model, transformations=[node_parser], show_progress=True)
            else:
                self.index = VectorStoreIndex.from_vector_store(vector_store, embed_model=self.embed_model)
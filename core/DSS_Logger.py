# core/DSS_Logger.py

import logging
import os
import json
from datetime import datetime
from core.ProjectContext import ProjectContext

class DSS_Logger:
    """
    A dedicated logger that records the entire interactive flow of a DSS session,
    capturing user inputs, raw AI responses, parsed AI analysis, and key decisions.
    """
    def __init__(self, log_directory="dss_logs"):
        os.makedirs(log_directory, exist_ok=True)
        self.log_filepath = None
        self.logger = None
        self.turn_counter = 0

    def create_log_file(self):
        """Creates a new, timestamped log file for the session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filepath = os.path.join("dss_logs", f"dss_session_{timestamp}.log")
        
        self.logger = logging.getLogger(f"DSS_Logger_{timestamp}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        handler = logging.FileHandler(self.log_filepath, encoding='utf-8')
        # Use a simpler formatter for cleaner multiline logs
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("="*25 + " DSS SESSION STARTED " + "="*25)
        self.logger.info(f"Log file: {self.log_filepath}")

    def log_step_start(self, step_name: str):
        if not self.logger: return
        self.logger.info("\n" + "="*20 + f" STARTING SPIDESOFT STEP: {step_name} " + "="*20)
        self.turn_counter = 0 # Reset for each new step

    def log_interaction_turn(self, user_input: str, raw_ai_response: str, parsed_ai_response: dict):
        if not self.logger: return
        self.turn_counter += 1
        
        self.logger.info("\n" + "-"*25 + f" INTERACTION TURN #{self.turn_counter} " + "-"*25)
        self.logger.info(f"[USER INPUT]\n{user_input}\n")
        
        # --- LOG THE RAW AI RESPONSE ---
        self.logger.info(f"[RAW AI (LLM) RESPONSE]\n{raw_ai_response}\n")
        
        # --- LOG THE PARSED AI ANALYSIS ---
        self.logger.info("[PARSED AI ANALYSIS]")
        self.logger.info(f"  - Refined Purpose: {parsed_ai_response.get('refined_purpose', 'N/A')}")
        
        stakeholders = parsed_ai_response.get('identified_stakeholders', {})
        if stakeholders:
            self.logger.info(f"  - ID'd Stakeholders: {json.dumps(stakeholders)}")

        self.logger.info(f"  - Analysis/Caution: {parsed_ai_response.get('analysis_and_caution', 'N/A')}")
        self.logger.info(f"  - Next Question: {parsed_ai_response.get('next_question', 'N/A')}")
        self.logger.info(f"  - Step Complete?: {parsed_ai_response.get('is_complete', False)}")
        self.logger.info("-" * 70)
        
    def log_user_decision(self, prompt: str, decision: bool):
        if not self.logger: return
        self.logger.info(f"\n[USER DECISION POINT]")
        self.logger.info(f"  - PROMPT: '{prompt}'")
        self.logger.info(f"  - CHOICE: {'Yes' if decision else 'No'}")

    def log_session_end(self, final_context: ProjectContext):
        if not self.logger: return
        self.logger.info("\n" + "="*25 + " DSS SESSION ENDED " + "="*25)
        self.logger.info("\n--- FINAL PROJECT CONTEXT ---")
        # Use the context's LLM summary method for a dense log output
        self.logger.info(final_context.get_summary_for_llm())
        self.logger.info("=" * 70)
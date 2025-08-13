# core/DSS_Logger.py

import logging
import os
import json
from datetime import datetime

class DSS_Logger:
    """A dedicated logger that records the entire flow of a DSS session into a unique file."""
    def __init__(self):
        self.log_filepath = None
        self.logger = None

    def start_session(self, project_name: str):
        """Creates and configures a new log file for the session."""
        log_directory = "dss_logs"
        os.makedirs(log_directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_project_name = project_name.replace(' ', '_').lower()
        self.log_filepath = os.path.join(log_directory, f"session_{safe_project_name}_{timestamp}.log")
        
        self.logger = logging.getLogger(f"DSS_Logger_{timestamp}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        handler = logging.FileHandler(self.log_filepath, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.info("="*25 + " DSS SESSION STARTED " + "="*25)
        self.info(f"Project: {project_name}")

    def info(self, message):
        if self.logger:
            self.logger.info(message)

    def error(self, message, exc_info=False):
        if self.logger:
            self.logger.error(message, exc_info=exc_info)

# In core/DSS_Logger.py, replace the existing log_turn method

    def log_turn(self, turn_number, user_input, raw_ai_response, parsed_ai_response, conversation_history):
        if not self.logger: return
        self.info("-" * 25 + f" INTERACTION TURN #{turn_number} " + "-" * 25)
        
        # --- NEW: Log the full conversation history sent to the model ---
        self.info("[FULL CONTEXT SENT TO LLM]")
        for message in conversation_history:
            # --- THE FIX IS HERE ---
            # ChatMessage objects have .role and .content attributes, not .get() methods.
            # This is now the correct and simple way to access the data.
            role = message.role
            content = message.content
            # --- END OF FIX ---
            self.info(f"  - ROLE: {str(role).upper()}\n    CONTENT: {content}\n")

        self.info(f"[USER'S LATEST INPUT]\n{user_input}\n")
        self.info(f"[RAW AI RESPONSE]\n{raw_ai_response}\n")
        self.info(f"[PARSED AI RESPONSE]\n{json.dumps(parsed_ai_response, indent=2)}\n")

    def end_session(self):
        self.info("=" * 25 + " DSS SESSION ENDED " + "=" * 25)
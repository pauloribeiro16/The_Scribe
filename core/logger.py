# core/logger.py
import os
import datetime
import logging

LOG_DIR_NAME = "evaluation_logs"

class TestLogger:
    """A dedicated class for logging RAG vs. No-RAG test results."""
    def __init__(self):
        self.log_filepath = None

    def initialize(self, model_name, source_name):
        log_dir = os.path.join(os.path.dirname(__file__), '..', LOG_DIR_NAME)
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_name = "".join(c for c in model_name if c.isalnum() or c in ('_')).replace(":", "_")
        safe_source_name = "".join(c for c in source_name if c.isalnum()).lower()
        
        self.log_filepath = os.path.join(log_dir, f"eval_{safe_source_name}_{safe_model_name}_{timestamp}.txt")
        
        header = [
            "="*60,
            f"             {source_name.upper()} RAG EVALUATION LOG",
            "="*60,
            f"MODEL: {model_name}",
            f"SOURCE: {source_name}",
            f"DATE: {datetime.datetime.now().isoformat()}",
            "="*60
        ]
        try:
            with open(self.log_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(header) + "\n\n")
            logging.info(f"Log file initialized at: {self.log_filepath}")
        except IOError as e:
            logging.error(f"Could not create log file: {e}")
            self.log_filepath = None

    def log_test_case(self, test_case, no_rag_result, rag_result, test_index):
        if not self.log_filepath: return
        
        lines = [
            f"------------------------------------------------------------",
            f"TEST CASE {test_index}: {test_case['category']}",
            f"------------------------------------------------------------",
            "QUESTION:",
            f"{test_case['question']}\n",
            "GOLDEN ANSWER:",
            f"{test_case['golden_answer']}\n",
            f"--- NO-RAG RESPONSE (took {no_rag_result['duration']:.2f} seconds) ---",
            f"  MODEL RESPONSE: {no_rag_result['response']}\n",
            f"--- RAG RESPONSE (took {rag_result['duration']:.2f} seconds) ---",
            f"  [DEBUG] CONTEXT SENT TO LLM:\n{rag_result['context']}\n",
            f"  MODEL RESPONSE: {rag_result['response']}\n",
            "="*60
        ]
        try:
            with open(self.log_filepath, 'a', encoding='utf-8') as f:
                f.write("\n".join(lines) + "\n\n")
        except IOError as e:
            logging.error(f"Could not write to log file: {e}")

    def log_summary(self, timings):
        if not self.log_filepath: return
        rag_times = timings.get('rag', [])
        no_rag_times = timings.get('no_rag', [])
        total_time = sum(rag_times) + sum(no_rag_times)
        avg_rag = sum(rag_times) / len(rag_times) if rag_times else 0
        avg_no_rag = sum(no_rag_times) / len(no_rag_times) if no_rag_times else 0
        
        summary = [
            "\n------------------------------------------------------------",
            "PERFORMANCE SUMMARY",
            "------------------------------------------------------------",
            f"Average RAG Response Time:       {avg_rag:.2f} seconds",
            f"Average No-RAG Response Time:    {avg_no_rag:.2f} seconds",
            f"Total Test Time:                 {total_time:.2f} seconds",
            "------------------------------------------------------------"
        ]
        try:
            with open(self.log_filepath, 'a', encoding='utf-8') as f:
                f.write("\n".join(summary))
        except IOError as e:
            logging.error(f"Could not write summary to log file: {e}")
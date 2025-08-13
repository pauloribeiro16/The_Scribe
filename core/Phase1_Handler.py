# core/Phase1_Handler.py (Corrected and Final Version)

import json
import beaupy
from core.ProjectContext import ProjectContext
from core.RAGEngine import RAGEngine
from llama_index.core.llms import ChatMessage, MessageRole
from core.DSS_Logger import DSS_Logger

class Phase1_Handler:
    def __init__(self, llm, rag_engine: RAGEngine, prompts: dict, logger: DSS_Logger):
        self.llm = llm
        self.rag_engine = rag_engine
        self.prompts = prompts
        self.logger = logger
        self.step_conversation_history = []

    # --- THE MISSING METHOD IS NOW HERE ---
    def _detect_user_intent(self, user_input: str) -> str:
        """Uses a simple heuristic to detect if the user is asking a question."""
        question_words = ["what", "how", "why", "who", "when", "where", "is", "are", "do", "does", "am"]
        normalized_input = user_input.lower().strip()
        if normalized_input.endswith('?') or any(normalized_input.startswith(word) for word in question_words):
            return "question"
        return "statement"
    # --- END OF FIX ---

    def _call_co_pilot_llm(self, user_input: str, system_prompt: str) -> dict:
        self.step_conversation_history.append(ChatMessage(role=MessageRole.USER, content=user_input))
        messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)] + self.step_conversation_history
        raw_content = "No response from LLM."
        try:
            response = self.llm.chat(messages=messages)
            raw_content = response.message.content
            self.step_conversation_history.append(response.message)
            
            json_start_index = raw_content.find('{')
            json_end_index = raw_content.rfind('}')
            
            if json_start_index == -1 or json_end_index == -1 or json_end_index < json_start_index:
                raise json.JSONDecodeError("Could not find a valid JSON object in the LLM response.", raw_content, 0)

            json_string = raw_content[json_start_index : json_end_index + 1]
            parsed_json = json.loads(json_string)
            return parsed_json
            
        except Exception as e:
            self.logger.error(f"Error processing LLM response. Raw content was:\n{raw_content}", exc_info=True)
            fallback = {
                "refined_purpose": "", "business_goals": [], "identified_stakeholders": {},
                "analysis_and_caution": "Error communicating with the AI. Please check the session log for details.",
                "next_question": "There was an error. Please try again, or type 'exit' to abort.",
                "is_complete": False
            }
            if not isinstance(self.step_conversation_history[-1].content, str):
                 self.step_conversation_history.append(ChatMessage(role=MessageRole.ASSISTANT, content=json.dumps(fallback)))
            return fallback

    def run_step_2_1(self, current_context: ProjectContext) -> ProjectContext:
        step_config = self.prompts.get("spidesoft_step_2_1", {})
        system_prompt = step_config.get("system_prompt")
        step_title = step_config.get('title', '2.1')
        self.logger.info(f"--- Starting Step: {step_title} ---")
        print(f"\n--- Starting Step: {step_title} ---")
        
        self.step_conversation_history = [
            ChatMessage(role=MessageRole.SYSTEM, content=f"MEMORY - Current Project Context:\n{current_context.get_summary_for_llm()}")
        ]
        
        if current_context.project_purpose:
            user_input = beaupy.prompt("What would you like to add or refine for this step?")
        else:
            user_input = beaupy.prompt("Let's define the project's purpose. To start, what is your initial idea?")

        turn_number = 0
        while True:
            turn_number += 1
            if user_input.lower() in ['exit', 'quit']: break
            
            parsed_ai_response = self._call_co_pilot_llm(user_input, system_prompt)
            self.logger.log_turn(
                turn_number, 
                user_input, 
                self.step_conversation_history[-1].content,
                parsed_ai_response,
                self.step_conversation_history
            )
            
            # --- DEFINITIVE DATA TYPE ENFORCEMENT FIX ---
            current_context.project_purpose = parsed_ai_response.get("refined_purpose", current_context.project_purpose)

            goals = parsed_ai_response.get("business_goals", current_context.business_goals)
            if isinstance(goals, str):
                current_context.business_goals = [g.strip() for g in goals.split(',') if g.strip()]
            elif isinstance(goals, list):
                current_context.business_goals = goals

            stakeholders = parsed_ai_response.get("identified_stakeholders", current_context.stakeholders)
            if isinstance(stakeholders, str):
                current_context.stakeholders = [s.strip() for s in stakeholders.split(',') if s.strip()]
            elif isinstance(stakeholders, dict) or isinstance(stakeholders, list):
                current_context.stakeholders = stakeholders
            # --- END OF FIX ---

            print("\n--- The Scribe Co-Pilot Analysis ---")
            print(f"Purpose: {current_context.project_purpose}")
            
            if current_context.business_goals:
                print(f"Business Goals: {', '.join(current_context.business_goals)}")

            if current_context.stakeholders:
                if isinstance(current_context.stakeholders, dict):
                    print(f"Stakeholders: {', '.join(current_context.stakeholders.keys())}")
                elif isinstance(current_context.stakeholders, list):
                    print(f"Stakeholders: {', '.join(current_context.stakeholders)}")

            print(f"⚠️ Caution: {parsed_ai_response.get('analysis_and_caution', '')}")
            
            is_step_complete = parsed_ai_response.get("is_complete", False)
            next_question = parsed_ai_response.get("next_question", "What would you like to add or change?")

            if is_step_complete:
                is_confirmed = beaupy.confirm(f"\n{next_question}", default_is_yes=True)
                if is_confirmed:
                    self.logger.info(f"User confirmed completion of Step {step_title}.")
                    print(f"\n✅ Step '{step_title}' confirmed as complete.")
                    break
                else:
                    self.logger.info("User chose to continue refining the step.")
                    user_input = beaupy.prompt("\nOkay, what would you like to add or change?")
            else:
                user_input = beaupy.prompt(f"\n{next_question}")

        current_context.conversation_logs[f"step_{step_title.split(':')[0]}"] = [
            {"role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role), "content": msg.content} 
            for msg in self.step_conversation_history if msg.role != MessageRole.SYSTEM
        ]
        return current_context
    
# In core/Phase1_Handler.py, replace the entire run_step_2_2 method

def run_step_2_2(self, current_context: ProjectContext) -> ProjectContext:
        """Runs the dialogue for Step 2.2 with the correct AI-initiated flow AND on-demand RAG."""
        step_config = self.prompts.get("spidesoft_step_2_2", {})
        system_prompt = step_config.get("system_prompt")
        step_title = step_config.get('title', '2.2')
        self.logger.info(f"--- Starting Step: {step_title} ---")
        print(f"\n--- Starting Step: {step_title} ---")

        if not current_context.completed_steps.get("2.1"):
            print("\n⚠️ Prerequisite Incomplete: Please complete Step 2.1 first.")
            return current_context

        context_summary = current_context.get_summary_for_llm()
        initial_memory = f"MEMORY - Current Project Context:\n{context_summary}"
        self.step_conversation_history = [ChatMessage(role=MessageRole.SYSTEM, content=initial_memory)]
        
        print("\nINFO: The Scribe is analyzing your project to suggest the first compliance topic...")
        initial_trigger = "Let's begin the compliance analysis. Based on the project context, what is the first topic we should discuss?"
        
        parsed_ai_response = self._call_co_pilot_llm(initial_trigger, system_prompt)
        self.logger.log_turn(1, "[AI Initiated Turn]", self.step_conversation_history[-1].content, parsed_ai_response, self.step_conversation_history)
        
        current_context.applicable_regulations = parsed_ai_response.get("identified_regulations", current_context.applicable_regulations)
        print("\n--- The Scribe's Compliance Analysis ---")
        if current_context.applicable_regulations:
            print(f"  - Confirmed Regulations: {', '.join(current_context.applicable_regulations)}")
        print(f"  - ⚠️ Analysis & Caution: {parsed_ai_response.get('analysis_and_caution', '')}")
        print("-" * 60)
        
        turn_number = 1
        while True:
            is_step_complete = parsed_ai_response.get("is_complete", False)
            next_question = parsed_ai_response.get("next_question", "How would you like to proceed?")

            if is_step_complete:
                if beaupy.confirm(f"\n{next_question}", default_is_yes=True): break
                else: user_input = beaupy.prompt("\nOkay, what would you like to add or change?")
            else:
                user_input = beaupy.prompt(f"\n{next_question}")

            turn_number += 1
            if user_input.lower() in ['exit', 'quit']: break
            
            # --- DEFINITIVE ON-DEMAND RAG FIX ---
            intent = self._detect_user_intent(user_input)
            llm_input = user_input
            
            if intent == "question":
                print("\n🔍 User asked a question. Conducting research...")
                self.logger.info(f"Detected user question. Triggering on-demand RAG for: '{user_input}'")
                
                rag_query = f"Regarding a project with context '{context_summary}', answer this specific user question: {user_input}"
                rag_results = self.rag_engine.query(rag_query, dss_logger=self.logger)
                rag_context = rag_results.get('context', 'No relevant information found.')
                
                llm_input = (
                    f"The user has asked a direct question: '{user_input}'\n\n"
                    f"Here is the research I found in my knowledge base:\n--- RESEARCH ---\n{rag_context}\n--- END RESEARCH ---\n\n"
                    f"Please answer their question using this research, then ask your next logical question to continue the compliance analysis."
                )
            # --- END OF FIX ---

            parsed_ai_response = self._call_co_pilot_llm(llm_input, system_prompt)
            self.logger.log_turn(turn_number, user_input, self.step_conversation_history[-1].content, parsed_ai_response, self.step_conversation_history)
            
            current_context.applicable_regulations = parsed_ai_response.get("identified_regulations", current_context.applicable_regulations)

            print("\n--- The Scribe's Compliance Analysis ---")
            if current_context.applicable_regulations:
                print(f"  - Confirmed Regulations: {', '.join(current_context.applicable_regulations)}")
            print(f"  - ⚠️ Analysis & Caution: {parsed_ai_response.get('analysis_and_caution', '')}")
            print("-" * 60)

        current_context.completed_steps["2.2"] = True
        print(f"\n✅ Step '{step_title}' confirmed as complete.")
        self.logger.info(f"User confirmed regulations: {current_context.applicable_regulations}")
        
        return current_context
# core/DSS_Session.py (Corrected with Stateful Conversation History and Exit Logic)

import beaupy
import json

from rpds import List
from core.ProjectContext import ProjectContext
from core.RAGEngine import RAGEngine
from llama_index.core.llms import ChatMessage, MessageRole
import logging
from core.DSS_Logger import DSS_Logger


SYSTEM_PROMPT_STEP_2_1 = """
You are "Cairn," an expert AI Systems Analyst and cybersecurity strategist. Your mission is to guide a user through **SPIDESOFT Step 2.1: Purpose and Stakeholders** through a disciplined, incremental, back-and-forth conversation.

**Your Core Directive: NEVER ASSUME. ALWAYS ASK.** Your goal is to help the user build the context piece by piece. You must not invent stakeholders or details the user has not provided.

**Your Guiding Process:**
You will be given the conversation history. At each turn, you must:

1.  **Analyze the User's LATEST Input:** Focus only on the new piece of information the user has just given you.
2.  **Integrate and Refine:** Update the current understanding of the purpose and stakeholders by integrating ONLY this new information. Rephrase it professionally.
3.  **Perform a DELTA Analysis:** What is the single most important piece of information that is now missing, based on the new context?
    *   If you don't know the **Industry** or **Location**, that is ALWAYS the top priority.
    *   If you have the industry/location, but no clear **Stakeholders**, ask for the primary user.
    *   If you have one stakeholder, ask for another (e.g., an administrator or an opposing force).
4.  **Ask a SINGLE, FOCUSED Question:** Formulate your `next_question` to elicit that one missing piece of information.

**CRITICAL RULE:** The `identified_stakeholders` in your JSON response must ONLY contain stakeholders that the user has explicitly mentioned in the conversation. DO NOT invent stakeholders like "Legal Team" or "External Malicious Actor" until the user introduces a concept that requires them.

**Example of CORRECT, Incremental Dialogue:**

-   **User Input:** "a portal for documents"
-   **Your Thought:** The user is vague. I don't know anything about the context. My top priority is to ask for the industry and location. I cannot assume any stakeholders yet.
-   **Your JSON Response:**
    ```json
    {
      "refined_purpose": "A portal for managing documents.",
      "identified_stakeholders": {},
      "analysis_and_caution": "This purpose is very broad. The specific security and privacy risks are currently unknown. The industry and user location are critical to determine compliance needs (e.g., GDPR for EU, HIPAA for healthcare).",
      "next_question": "To start, what is the primary industry this portal will be used in (e.g., healthcare, finance, manufacturing), and where are its users primarily located (e.g., EU, USA)?",
      "is_complete": false
    }
    ```

-   **User Input:** "it is for a healthcare company in the eu"
-   **Your Thought:** Excellent. Now I have critical context. Healthcare + EU immediately means GDPR and PHI are in scope. The purpose is now about *healthcare* documents. I still don't know who the users are. That's the next most important question.
-   **Your JSON Response:**
    ```json
    {
      "refined_purpose": "A portal for managing healthcare documents for a company based in the EU.",
      "identified_stakeholders": {},
      "analysis_and_caution": "The context of 'Healthcare' and 'EU' is critical. This system will be subject to GDPR and must be designed to protect Protected Health Information (PHI). Unauthorized access could have severe legal and patient safety consequences.",
      "next_question": "Understood. Who are the primary users who will be accessing these healthcare documents? (e.g., Patients, Doctors, Researchers)",
      "is_complete": false
    }
    ```

**Output Format:** You MUST respond with only a JSON object. The `identified_stakeholders` key must follow the detailed structure, but only for stakeholders the user has mentioned.
"""


class DSS_Session:
    def __init__(self, llm, rag_engine: RAGEngine):
        self.llm = llm
        self.rag_engine = rag_engine
        self.context = ProjectContext()
        self.logger = DSS_Logger()
        # This will now store the history for a single step
        self.step_conversation_history: List[ChatMessage] = []

    def _call_co_pilot_llm(self, user_input: str, system_prompt: str) -> tuple[str, dict]:
        """Calls the LLM with the system prompt and the CURRENT conversation history."""
        
        # --- STATEFUL CONVERSATION FIX ---
        # Add the new user message to the history
        self.step_conversation_history.append(ChatMessage(role=MessageRole.USER, content=user_input))
        
        # Construct the full message list for the API call
        messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)] + self.step_conversation_history
        # --- END OF FIX ---

        raw_content = ""
        try:
            response = self.llm.chat(messages=messages)
            raw_content = response.message.content
            
            # Add the assistant's response to our history to maintain state
            self.step_conversation_history.append(response.message)
            
            json_start_index = raw_content.find('{')
            if json_start_index == -1: raise json.JSONDecodeError("No JSON object found", raw_content, 0)
            json_string = raw_content[json_start_index:]
            
            if json_string.strip().startswith("```json"):
                json_string = json_string.strip()[7:-3]
            elif json_string.strip().startswith("```"):
                 json_string = json_string.strip()[3:-3]
            
            parsed_json = json.loads(json_string)
            return raw_content, parsed_json
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            logging.error(f"Error processing LLM response: {e}\nRaw Content: {raw_content[:500]}")
            fallback_json = {
                "refined_purpose": "Error: Could not parse AI response.", "identified_stakeholders": {},
                "analysis_and_caution": "The AI Co-Pilot returned an invalid format.",
                "next_question": "Could you please try again?", "is_complete": False
            }
            # Add a placeholder to history so the loop can continue
            self.step_conversation_history.append(ChatMessage(role=MessageRole.ASSISTANT, content=json.dumps(fallback_json)))
            return raw_content, fallback_json

    def _run_step_2_1_purpose_and_stakeholders(self):
        """Interactively and iteratively define the project purpose and stakeholders."""
        step_name = "2.1 Purpose & Stakeholders"
        self.logger.log_step_start(step_name)
        # Clear the history for this new step
        self.step_conversation_history = []
        
        print("\n" + "="*15 + f" SPIDESOFT Step {step_name} " + "="*15)
        print("Let's define the project's core purpose. The AI will help refine it.")
        print("You can type 'exit' or 'quit' at any time to end the session.")
        
        user_input = beaupy.prompt("To start, in a few words, what is the purpose of your project?")
        
        while True:
            # --- ABORT SESSION LOGIC ---
            if user_input.lower() in ['exit', 'quit']:
                print("Session aborted by user.")
                break
            # --- END OF ABORT LOGIC ---

            raw_ai_response, parsed_ai_response = self._call_co_pilot_llm(user_input, SYSTEM_PROMPT_STEP_2_1)
            self.logger.log_interaction_turn(user_input, raw_ai_response, parsed_ai_response)

            self.context.project_purpose = parsed_ai_response.get("refined_purpose", self.context.project_purpose)
            self.context.stakeholders = parsed_ai_response.get("identified_stakeholders", self.context.stakeholders)

            print("\n" + "-"*60); print("SPIDSOFT CO-PILOT ANALYSIS:")
            print(f"  - Purpose: {self.context.project_purpose}")
            if self.context.stakeholders:
                print("  - Stakeholders:")
                for role, concern in self.context.stakeholders.items(): print(f"    - {role}: {concern}")
            print(f"  - ⚠️ Caution: {parsed_ai_response.get('analysis_and_caution', '')}"); print("-"*60)
            
            is_step_complete = parsed_ai_response.get("is_complete", False)
            next_question = parsed_ai_response.get("next_question", "What would you like to add or change?")

            if is_step_complete:
                confirmation_prompt = "The Co-Pilot suggests this section is complete. Do you agree?"
                is_confirmed = beaupy.confirm(f"\n{confirmation_prompt}", default_is_yes=True)
                self.logger.log_user_decision(confirmation_prompt, is_confirmed)
                if is_confirmed:
                    print("\n✅ Great! Purpose and Stakeholders have been defined."); break
                else:
                    user_input = beaupy.prompt("\nOkay, what would you like to add or change?")
            else:
                user_input = beaupy.prompt(f"\n{next_question}")

    def start_session(self):
        """Starts and orchestrates the entire SPIDESOFT DSS session."""
        self.logger.create_log_file()
        print("\n" + "="*20 + " SPIDESOFT DSS Co-Pilot Session Started " + "="*20)
        print(f"INFO: A detailed log for this session is being recorded in: {self.logger.log_filepath}")
        
        self._run_step_2_1_purpose_and_stakeholders()
        
        print("\n" + "="*20 + " End of Current Session " + "="*20)
        self.context.display_summary()
        self.logger.log_session_end(self.context)
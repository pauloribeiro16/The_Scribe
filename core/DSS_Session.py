# core/DSS_Session.py

import os
import json
import beaupy
from core.ProjectContext import ProjectContext
from core.RAGEngine import RAGEngine
from core.Phase1_Handler import Phase1_Handler
from core.DSS_Logger import DSS_Logger

class DSS_Session:
    def __init__(self, llm, rag_engine: RAGEngine):
        self.llm = llm
        self.rag_engine = rag_engine
        self.context = ProjectContext()
        self.project_filepath = None
        self.logger = DSS_Logger()
        os.makedirs("projects", exist_ok=True)

    # ... (_load_prompts, load_project, save_project methods remain the same) ...
    def _load_prompts(self):
        try:
            with open("core/prompts.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error("`prompts.json` file not found or is invalid.", exc_info=True)
            print("Error: `prompts.json` file not found or is invalid. Please check the file. Exiting.")
            exit()
            
    def _select_project(self):
        project_files = [f for f in os.listdir("projects") if f.endswith(".json")]
        menu_options = ["<Create a New Project>"] + project_files
        print("\nPlease select a project or create a new one:")
        selection = beaupy.select(menu_options)
        if not selection: return False
        if selection == "<Create a New Project>":
            project_name = beaupy.prompt("Enter the name for your new project:")
            if not project_name: return False
            self.context.project_name = project_name
            self.project_filepath = os.path.join("projects", f"{project_name.replace(' ', '_').lower()}.json")
            self.logger.start_session(project_name) # Start logging
            self.save_project()
        else:
            self.project_filepath = os.path.join("projects", selection)
            self.load_project()
            self.logger.start_session(self.context.project_name) # Start logging
        print(f"INFO: Detailed log for this session is being recorded in: {self.logger.log_filepath}")
        return True

    def load_project(self):
        """Loads the project context from its JSON file using the from_dict method."""
        try:
            with open(self.project_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.context = ProjectContext.from_dict(data) # Use the new class method
                print(f"\n✅ Project '{self.context.project_name}' loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Could not find project file at {self.project_filepath}")

    def save_project(self):
        """Saves the current project context to its JSON file using the to_dict method."""
        if not self.project_filepath:
            print("Error: No project file path set. Cannot save.")
            return

        with open(self.project_filepath, 'w', encoding='utf-8') as f:
            # Use the new instance method to get all data
            json.dump(self.context.to_dict(), f, indent=2) 
        self.logger.info(f"Project state saved to {self.project_filepath}")
        print(f"✅ Project saved to {self.project_filepath}")
            
# In core/DSS_Session.py, replace the entire start_session method

    def start_session(self):
        """Starts and orchestrates the entire SPIDESOFT DSS session."""
        print("\n" + "="*20 + " SPIDESOFT DSS Co-Pilot Session Started " + "="*20)
        
        if not self._select_project():
            return
        
        prompts = self._load_prompts()
        
        phase1_handler = Phase1_Handler(self.llm, self.rag_engine, prompts, self.logger)
        # phase2_handler = Phase2_Handler(...) # For the future

        while True:
            print("\n--- The Scribe Co-Pilot Menu ---")
            self.context.display_summary()
            
            menu = [
                "1. Run Step 2.1: Purpose & Stakeholders",
                "2. Run Step 2.2: Legal & Regulatory Compliance",
                "3. Save Project and Return to Main Menu"
            ]
            
            # --- THE MISSING LINE IS HERE ---
            choice = beaupy.select(menu)
            # --- END OF FIX ---
            
            if not choice or "Save Project" in choice:
                self.save_project()
                break

            if "Step 2.1" in choice:
                self.context = phase1_handler.run_step_2_1(self.context)
                # Mark step as complete after the run
                self.context.completed_steps["2.1"] = True
                self.save_project()
            
            elif "Step 2.2" in choice:
                self.context = phase1_handler.run_step_2_2(self.context)
                self.context.completed_steps["2.2"] = True
                self.save_project()

        self.logger.end_session()
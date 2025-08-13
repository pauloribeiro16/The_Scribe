# core/ProjectContext.py

class ProjectContext:
    def __init__(self):
        self.project_name: str = ""
        self.project_purpose: str = ""
        self.business_goals: list[str] = []
        self.stakeholders: dict = {}
        self.conversation_logs: dict = {}
        # NEW: Add completed_steps attribute
        self.completed_steps: dict = {}
        # ... other attributes ...

    def to_dict(self) -> dict:
        """Serializes the entire project context to a dictionary for saving."""
        return {
            "project_name": self.project_name,
            "project_purpose": self.project_purpose,
            "business_goals": self.business_goals,
            "stakeholders": self.stakeholders,
            "conversation_logs": self.conversation_logs,
            # NEW: Include completed_steps in serialization
            "completed_steps": self.completed_steps,
            "applicable_regulations": self.applicable_regulations,
            "data_inventory": self.data_inventory,
            "privacy_goals": self.privacy_goals,
            "security_goals": self.security_goals,
            "is_complete": self.is_complete
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a ProjectContext instance from a dictionary."""
        context = cls()
        context.project_name = data.get("project_name", "")
        context.project_purpose = data.get("project_purpose", "")
        context.business_goals = data.get("business_goals", [])
        context.stakeholders = data.get("stakeholders", {})
        context.conversation_logs = data.get("conversation_logs", {})
        # NEW: Include completed_steps in deserialization
        context.completed_steps = data.get("completed_steps", {})
        context.applicable_regulations = data.get("applicable_regulations", [])
        context.data_inventory = data.get("data_inventory", {})
        context.privacy_goals = data.get("privacy_goals", [])
        context.security_goals = data.get("security_goals", {'Confidentiality': '', 'Integrity': '', 'Availability': ''})
        context.is_complete = data.get("is_complete", False)
        return context

    def display_summary(self):
        """Prints a user-friendly summary of the collected context, now with robust type handling."""
        print("\n" + "="*20 + " SPIDESOFT Phase 1 Summary " + "="*20)
        print(f"Project Name: {self.project_name}")
        
        if self.project_purpose:
            print(f"\nPurpose: {self.project_purpose}")

        # --- ROBUST DISPLAY FIX FOR BUSINESS GOALS ---
        if self.business_goals:
            print("\n--- Business Goals ---")
            # Handle both list and string data types safely
            if isinstance(self.business_goals, list):
                for goal in self.business_goals:
                    print(f"- {goal}")
            elif isinstance(self.business_goals, str):
                print(f"- {self.business_goals}")
        # --- END OF FIX ---

        # --- ROBUST DISPLAY FIX FOR STAKEHOLDERS ---
        if self.stakeholders:
            print("\n--- Stakeholders & Concerns ---")
            # Handle dict, list, and string data types safely
            if isinstance(self.stakeholders, dict):
                for role, details in self.stakeholders.items():
                    print(f"- {role}: {details}")
            elif isinstance(self.stakeholders, list):
                print(f"- {', '.join(self.stakeholders)}")
            elif isinstance(self.stakeholders, str):
                print(f"- {self.stakeholders}")
        print("="*65)

# In core/ProjectContext.py, replace the entire get_summary_for_llm method

    def get_summary_for_llm(self) -> str:
        """Generates a concise summary for the AI's memory, with robust type handling."""
        
        # --- ROBUST SUMMARY FIX FOR BUSINESS GOALS ---
        goals_summary = ""
        if isinstance(self.business_goals, list):
            # If it's a list, join it properly.
            goals_summary = "; ".join(self.business_goals)
        elif isinstance(self.business_goals, str):
            # If it's a string, use it directly. DO NOT iterate over it.
            goals_summary = self.business_goals
        # --- END OF FIX ---

        # --- ROBUST SUMMARY FIX FOR STAKEHOLDERS ---
        stakeholder_summary = ""
        if isinstance(self.stakeholders, dict):
            stakeholder_summary = "; ".join(self.stakeholders.keys())
        elif isinstance(self.stakeholders, list):
            stakeholder_summary = "; ".join(self.stakeholders)
        elif isinstance(self.stakeholders, str):
            # If it's a string, use it directly.
            stakeholder_summary = self.stakeholders
        # --- END OF FIX ---

        return (
            f"Project Name: '{self.project_name}'.\n"
            f"Purpose: '{self.project_purpose}'.\n"
            f"Business Goals: '{goals_summary}'.\n"
            f"Stakeholders: '{stakeholder_summary}'."
        )
# core/ProjectContext.py

class ProjectContext:
    """
    Holds the context of the software project, aligned with the
    SPIDESOFT methodology's Phase 1 artifacts.
    """
    def __init__(self):
        # --- Step 2.1: Purpose & Stakeholders ---
        self.project_name: str = ""
        self.project_purpose: str = "" # The "why"
        self.stakeholders: dict = {} # e.g., {'Patients': 'Concerns about data privacy'}

        # --- Step 2.2: Legal & Regulatory ---
        self.applicable_regulations: list[str] = []

        # --- Step 2.3: Data Minimization ---
        self.data_inventory: dict = {} # e.g., {'Patient Name': 'Required for identification'}

        # --- Step 2.4: Privacy Goals ---
        self.privacy_goals: list[str] = []

        # --- Step 2.5: Security Goals (CIA) ---
        self.security_goals: dict = {'Confidentiality': '', 'Integrity': '', 'Availability': ''}

        self.is_complete: bool = False

    def get_summary_for_llm(self) -> str:
        """Generates a concise summary formatted for an LLM prompt for the next phase."""
        if not self.is_complete:
            return "Project context is not yet complete."
            
        stakeholder_summary = "; ".join([f"{role}: {concern}" for role, concern in self.stakeholders.items()])
        data_summary = "; ".join([f"{item}: {justification}" for item, justification in self.data_inventory.items()])

        return (
            f"The system is named '{self.project_name}' with the purpose: '{self.project_purpose}'. "
            f"Key stakeholders and their concerns are: {stakeholder_summary}. "
            f"It must comply with the following regulations: {', '.join(self.applicable_regulations)}. "
            f"The data being processed includes: {data_summary}. "
            f"High-level privacy goals are: {', '.join(self.privacy_goals)}. "
            f"The primary security goals are: Confidentiality - {self.security_goals['Confidentiality']}; "
            f"Integrity - {self.security_goals['Integrity']}; Availability - {self.security_goals['Availability']}."
        )

    def display_summary(self):
        """Prints a user-friendly summary of the collected context."""
        print("\n" + "="*20 + " SPIDESOFT Phase 1 Summary " + "="*20)
        print(f"Project Name: {self.project_name}")
        print(f"Purpose: {self.project_purpose}")
        
        print("\n--- Stakeholders & Concerns ---")
        for role, concern in self.stakeholders.items():
            print(f"- {role}: {concern}")
            
        print("\n--- Legal & Regulatory Compliance ---")
        print(f"Applicable Regulations: {', '.join(self.applicable_regulations)}")

        print("\n--- Data Inventory (Data Minimization) ---")
        for item, justification in self.data_inventory.items():
            print(f"- {item}: {justification}")
            
        print("\n--- High-Level Privacy Goals ---")
        for goal in self.privacy_goals:
            print(f"- {goal}")
            
        print("\n--- Foundational Security Goals (CIA) ---")
        print(f"- Confidentiality: {self.security_goals['Confidentiality']}")
        print(f"- Integrity: {self.security_goals['Integrity']}")
        print(f"- Availability: {self.security_goals['Availability']}")
        print("="*65)
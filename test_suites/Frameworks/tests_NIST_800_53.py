# test_suites/tests_nist_sp_800_53r5.py

# A test suite for the full NIST SP 800-53 Revision 5 document.
TEST_CASES_NIST_SP_800_53R5 = [
    { 
        "category": "Control Purpose", 
        "question": "What is the purpose of the AC-1 (Policy and Procedures) control in the Access Control family?",
        "golden_answer": "The AC-1 control requires an organization to develop, document, and disseminate an access control policy and procedures. The policy addresses purpose, scope, roles, responsibilities, and compliance, while the procedures facilitate the implementation of the policy and its associated controls. It is a foundational control for the Access Control family."
    },
    {
        "category": "Control Enhancement Detail",
        "question": "What is the purpose of the 'Dynamic Privilege Management' enhancement for control AC-2 (Account Management)?",
        "golden_answer": "The AC-2(6) 'Dynamic Privilege Management' enhancement addresses runtime access control decisions. It includes capabilities like immediate revocation of privileges without requiring a user to restart a session, and automatic adjustment of privileges based on dynamic rules, such as time of day or if a system is under duress."
    },
    {
        "category": "Specific Security Concept",
        "question": "According to the discussion in control SI-14 (Non-Persistence), how does this control help mitigate the Advanced Persistent Threat (APT)?",
        "golden_answer": "The discussion for SI-14 states that non-persistence mitigates risk from APTs by reducing the adversary's window of opportunity and available attack surface. By periodically refreshing or terminating system components and services from a known state, it prevents adversaries from having sufficient time to exploit vulnerabilities and increases their work factor."
    },
    {
        "category": "Privacy Control Detail",
        "question": "What does the PT-4 (Consent) control require an organization to do regarding Personally Identifiable Information (PII)?",
        "golden_answer": "The PT-4 control requires an organization to implement tools or mechanisms for individuals to consent to the processing of their PII *prior* to its collection. The goal is to facilitate individuals’ informed decision-making about the processing of their information."
    }
]
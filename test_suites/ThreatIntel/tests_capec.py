# test_suites/tests_capec.py
TEST_CASES_CAPEC = [
    { 
        "category": "Attack Pattern Definition", 
        "question": "What is CAPEC-66: SQL Injection, and what are its typical consequences?",
        "golden_answer": "SQL Injection is an attack technique used to exploit vulnerabilities in the database layer of an application. The attacker injects malicious SQL statements into an entry field for execution. The typical consequences include unauthorized access to data, modification or deletion of data, and potentially full control over the application or database server."
    },
    {
        "category": "Framework Relationships",
        "question": "According to the CAPEC data, what are the main CWE weaknesses related to CAPEC-115: Authentication Bypass?",
        "golden_answer": "The primary related Common Weakness Enumeration (CWE) for authentication bypass includes weaknesses such as CWE-287 (Improper Authentication) and CWE-306 (Missing Authentication for Critical Function)."
    }
]
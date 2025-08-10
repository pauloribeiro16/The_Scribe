# test_suites/tests_cwe.py
TEST_CASES_CWE = [
    { 
        "category": "Core Definition", 
        "question": "What is CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')?",
        "golden_answer": "This weakness occurs when software constructs all or part of an SQL command using external input from an untrusted source, which can allow an attacker to modify the syntax of the command. The main consequence is that the attacker can view, modify, or delete database records."
    },
    {
        "category": "Relationships",
        "question": "What are the related CAPEC attack patterns for CWE-79: Cross-Site Scripting (XSS)?",
        "golden_answer": "Related attack patterns for XSS include CAPEC-18, CAPEC-19, CAPEC-244, CAPEC-588, CAPEC-591, and CAPEC-63, which describe various methods of injecting and executing malicious scripts in a user's web browser."
    }
]
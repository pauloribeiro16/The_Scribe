# test_suites/tests_nist_csf2_functions.py

TEST_CASES_NIST_CSF2 = [
    { 
        "category": "High-Level Function Summary", 
        "question": "What are the main goals of the GOVERN function in the NIST CSF 2.0?",
        "golden_answer": "The GOVERN function's goals are to establish, communicate, and monitor the organization’s cybersecurity risk management strategy, expectations, and policy. It informs and prioritizes the other five functions and integrates cybersecurity into the broader enterprise risk management (ERM) strategy."
    },
    {
        "category": "Category Listing",
        "question": "List the categories within the PROTECT function of the NIST CSF 2.0.",
        "golden_answer": "The categories within the PROTECT function are: Identity Management, Authentication, and Access Control (PR.AA); Awareness and Training (PR.AT); Data Security (PR.DS); Platform Security (PR.PS); and Technology Infrastructure Resilience (PR.IR)."
    },
    {
        "category": "Function Purpose",
        "question": "What is the purpose of the DETECT function in the CSF 2.0?",
        "golden_answer": "The DETECT function enables the timely discovery and analysis of anomalies, indicators of compromise, and other potentially adverse events. Its goal is to find and analyze possible cybersecurity attacks and compromises, which supports successful incident response and recovery activities."
    }
]
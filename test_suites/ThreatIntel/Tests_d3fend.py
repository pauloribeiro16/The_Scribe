# test_suites/Tests_d3fend.py
TEST_CASES_D3FEND = [
    { 
        "category": "Core Definition", 
        "question": "What is 'File Encryption' (D3-FE) according to D3FEND?",
        "golden_answer": "File Encryption is a data encryption technique where a file's data is encoded to prevent unauthorized access. It directly protects the confidentiality of data at rest."
    },
    {
        "category": "Internal Relationship (Hierarchy)",
        "question": "What are some specific types of 'Network Traffic Filtering' mentioned in D3FEND?",
        "golden_answer": "Specific types of Network Traffic Filtering include Packet Filtering, Stateful Filtering, and Stateless Filtering. These techniques inspect network packets and permit or deny them based on a set of rules."
    },
    {
        "category": "External Relationship (ATT&CK)",
        "question": "Which MITRE ATT&CK technique does the D3FEND technique 'Decoy Credentials' primarily counter?",
        "golden_answer": "The 'Decoy Credentials' (D3-DC) technique primarily counters the MITRE ATT&CK technique T1003: OS Credential Dumping. It involves creating fake credentials to detect when an adversary attempts to steal and use them."
    },
    {
        "category": "ID-based Query",
        "question": "What is the defensive technique associated with the ID D3-AL?",
        "golden_answer": "D3-AL corresponds to the 'Account Locking' technique, which is a method of credential eviction used to temporarily disable user accounts, often in response to repeated failed login attempts."
    },
    {
        "category": "Tactic-based Query",
        "question": "What are some defensive techniques that enable the 'Deceive' tactic in D3FEND?",
        "golden_answer": "Defensive techniques that enable the 'Deceive' tactic include Decoy Object, Decoy Credentials, Decoy File, Honeytoken, and Decoy Process."
    }
]
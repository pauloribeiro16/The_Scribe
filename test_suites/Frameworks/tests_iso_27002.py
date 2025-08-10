# test_suites/tests_iso_27002.py

TEST_CASES_ISO_27002 = [
    { 
        "category": "Organizational Control", 
        "question": "What is the purpose of control 5.7 Threat intelligence in ISO 27002?",
        "golden_answer": "The purpose of Threat Intelligence is to provide awareness of the organization’s threat environment so that the appropriate mitigation actions can be taken."
    },
    {
        "category": "People Control",
        "question": "According to ISO 27002, what should be considered for remote working under control 6.7?",
        "golden_answer": "For remote working, security measures should be implemented to protect information accessed, processed, or stored outside the organization’s premises. This includes considering the physical security of the remote site, communication security requirements, and the threat of unauthorized access from others at the remote location."
    },
    {
        "category": "Physical Control",
        "question": "What does the guidance for control 7.7 Clear desk and clear screen recommend?",
        "golden_answer": "The guidance recommends locking away sensitive or critical information when not required, protecting user endpoint devices with locks or screen savers when unattended, collecting printouts immediately, and securely storing or disposing of documents and removable media."
    },
    {
        "category": "Technological Control",
        "question": "What is the purpose of control 8.12 Data leakage prevention in ISO 27002?",
        "golden_answer": "The purpose is to detect and prevent the unauthorized disclosure and extraction of information by individuals or systems. This involves applying measures to systems, networks, and devices that process, store, or transmit sensitive information."
    }
]
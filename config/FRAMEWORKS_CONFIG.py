# config/sources.py
import os

# ---> IMPORT THE NEW PARSER AND TEST SUITE
from parsers.Frameworks.parse_nist_800_53b import parse_nist_sp_800_53r5

from test_suites.Frameworks.tests_NIST_800_53 import TEST_CASES_NIST_SP_800_53R5
from test_suites.Frameworks.tests_nist_csf2 import TEST_CASES_NIST_CSF2
from parsers.Frameworks.parse_nist_csf2 import parse_nist_csf2
from parsers.Frameworks.parse_iso_27002 import parse_iso_27002
from test_suites.Frameworks.tests_iso_27002 import TEST_CASES_ISO_27002

# Define the base path to the documents folder
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')

# Configuration dictionary for all data sources
Frameworks_CONFIG = {
    "NIST SP 800-53 Rev. 5": {
        "name": "NIST SP 800-53 Rev. 5",
        "parser": parse_nist_sp_800_53r5,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIST.SP.800-53r5.txt"),
        "collection_name": "nist80053r5_v1_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_NIST_SP_800_53R5,
        "system_prompt": "You are an expert in cybersecurity compliance. Answer questions about security controls based on the provided NIST SP 800-53 context."
    },
    "NIST CSF 2.0": {
        "name": "NIST CSF 2.0",
        "parser": parse_nist_csf2,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NISTCSWP29.txt"), # <-- CORRIGIDO
        "collection_name": "nist_csf2_v1_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_NIST_CSF2,
        "system_prompt": "You are an expert in cybersecurity risk management. Answer questions based on the provided NIST Cybersecurity Framework (CSF) 2.0 context."
    },
    "ISO/IEC 27002:2022": {
        "name": "ISO/IEC 27002:2022",
        "parser": parse_iso_27002,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "ISO_27002.txt"),
        "collection_name": "iso_27002_v1_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_ISO_27002,
        "system_prompt": "You are an information security specialist. Answer questions about security controls based on the provided ISO/IEC 27002:2022 context."
    },

}
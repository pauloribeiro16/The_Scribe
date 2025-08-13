# config/knowledge_bases_config.py

import os

# --- IMPORT ALL PARSERS ---
from parsers.ThreatIntel.parse_cwe_xml import parse_cwe_from_xml
from parsers.ThreatIntel.parse_capec_xml import parse_capec_from_xml
from parsers.ThreatIntel.parse_d3fend_ttl import parse_d3fend_from_ttl
from parsers.Frameworks.parse_nist_800_53b import parse_nist_sp_800_53r5
from parsers.Frameworks.parse_nist_csf2 import parse_nist_csf2
from parsers.Frameworks.parse_iso_27002 import parse_iso_27002
from parsers.Regulations.parse_gdpr import parse_gdpr_from_text
from parsers.Regulations.parse_dora import parse_dora_from_text
from parsers.Regulations.parse_nis2 import parse_nis2_from_text


# --- IMPORT ALL TEST SUITES ---
from test_suites.ThreatIntel.tests_cwe import TEST_CASES_CWE
from test_suites.ThreatIntel.tests_capec import TEST_CASES_CAPEC
from test_suites.ThreatIntel.Tests_d3fend import TEST_CASES_D3FEND
from test_suites.Frameworks.tests_NIST_800_53 import TEST_CASES_NIST_SP_800_53R5
from test_suites.Frameworks.tests_nist_csf2 import TEST_CASES_NIST_CSF2
from test_suites.Frameworks.tests_iso_27002 import TEST_CASES_ISO_27002
from test_suites.Regulations.tests_gdpr import TEST_CASES_GDPR
from test_suites.Regulations.tests_dora import TEST_CASES_DORA
from test_suites.Regulations.tests_nis2 import TEST_CASES_NIS2
from test_suites.Basics.tests_csslp_guide import TEST_CASES_CSSLP_GUIDE

# Define the base path to the documents folder
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')

# ==============================================================================
# CATEGORY DEFINITIONS FOR THE ROUTER
# ==============================================================================
CATEGORY_DESCRIPTIONS = {
    "Regulations": "Contains legal and regulatory mandates (GDPR, DORA, NIS2). Use for questions on legal obligations and compliance.",
    "Frameworks": "Contains security control standards (NIST CSF, NIST 800-53, ISO 27002). Use for questions on implementing security programs and risk management.",
    "Threat Intelligence": "Contains technical catalogs of weaknesses (CWE), attack patterns (CAPEC), and defenses (D3FEND). Use for questions on how attacks work and technical countermeasures.",
    "Basics": "Contains foundational knowledge like the CSSLP guide for general questions about secure software development principles."
}

# ==============================================================================
# THE SINGLE SOURCE OF TRUTH FOR ALL KNOWLEDGE BASES
# ==============================================================================
ALL_KNOWLEDGE_BASES = {
    # === CATEGORY: REGULATIONS ===
    "GDPR": {
        "category": "Regulations",
        "name": "GDPR",
        "description": "A European Union regulation on data protection and privacy for all individuals within the EU.",
        "parser": parse_gdpr_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "GDPR.txt"),
        "collection_name": "gdpr_v1_modular",
        "system_prompt": "You are a legal assistant specializing in GDPR. Answer questions based on the provided text.",
        "test_cases": TEST_CASES_GDPR,
    },
    "DORA": {
        "category": "Regulations",
        "name": "DORA (Digital Operational Resilience Act)",
        "description": "A European Union regulation for the financial sector focusing on digital operational resilience.",
        "parser": parse_dora_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "DORA.txt"),
        "collection_name": "dora_v1_modular",
        "system_prompt": "You are a compliance expert for the financial sector. Answer based on the provided DORA text.",
        "test_cases": TEST_CASES_DORA,
    },
    "NIS2 Directive": {
        "category": "Regulations",
        "name": "NIS2 Directive",
        "description": "A European Union directive on cybersecurity for critical infrastructure sectors.",
        "parser": parse_nis2_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIS2.txt"),
        "collection_name": "nis2_v1_modular",
        "system_prompt": "You are an expert on EU cybersecurity legislation. Answer based on the provided NIS2 Directive text.",
        "test_cases": TEST_CASES_NIS2,
    },

    # === CATEGORY: FRAMEWORKS ===
    "NIST SP 800-53 Rev. 5": {
        "category": "Frameworks",
        "name": "NIST SP 800-53 Rev. 5",
        "description": "A comprehensive catalog of security and privacy controls for U.S. federal information systems.",
        "parser": parse_nist_sp_800_53r5,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIST.SP.800-53r5.txt"),
        "collection_name": "nist80053r5_v1_modular",
        "system_prompt": "You are an expert in cybersecurity compliance. Answer based on the provided NIST SP 800-53 context.",
        "test_cases": TEST_CASES_NIST_SP_800_53R5,
    },
    "NIST CSF 2.0": {
        "category": "Frameworks",
        "name": "NIST CSF 2.0",
        "description": "A high-level framework for managing cybersecurity risk, organized by Govern, Identify, Protect, Detect, Respond, and Recover.",
        "parser": parse_nist_csf2,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NISTCSWP29.txt"),
        "collection_name": "nist_csf2_v1_modular",
        "system_prompt": "You are an expert in cybersecurity risk management. Answer based on the NIST CSF 2.0 context.",
        "test_cases": TEST_CASES_NIST_CSF2,
    },
    "ISO/IEC 27002:2022": {
        "category": "Frameworks",
        "name": "ISO/IEC 27002:2022",
        "description": "An international standard providing a catalog of information security controls to support an ISO 27001 ISMS.",
        "parser": parse_iso_27002,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "ISO_27002.txt"),
        "collection_name": "iso_27002_v1_modular",
        "system_prompt": "You are an information security specialist. Answer based on the ISO/IEC 27002:2022 context.",
        "test_cases": TEST_CASES_ISO_27002,
    },

    # === CATEGORY: THREAT INTELLIGENCE ===
    "CWE": {
        "category": "Threat Intelligence",
        "name": "CWE (Common Weakness Enumeration)",
        "description": "A list of common software and hardware weakness types (e.g., CWE-79 for Cross-Site Scripting).",
        "parser": parse_cwe_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "cwec_latest.xml"),
        "collection_name": "cwe_xml_modular",
        "system_prompt": "You are an expert in software vulnerabilities. Answer based on the provided CWE context.",
        "test_cases": TEST_CASES_CWE,
    },
    "CAPEC": {
        "category": "Threat Intelligence",
        "name": "CAPEC (Common Attack Pattern Enumeration and Classification)",
        "description": "A dictionary of known patterns of attack used by adversaries.",
        "parser": parse_capec_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "capec_latest.xml"),
        "collection_name": "capec_xml_modular",
        "system_prompt": "You are an expert in attack patterns. Answer based on the provided CAPEC context.",
        "test_cases": TEST_CASES_CAPEC,
    },
    "D3FEND": {
        "category": "Threat Intelligence",
        "name": "D3FEND",
        "description": "A knowledge graph of defensive cybersecurity techniques and countermeasures.",
        "parser": parse_d3fend_from_ttl,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "d3fend.txt"),
        "collection_name": "d3fend_ontology_modular",
        "system_prompt": "You are an expert in the D3FEND ontology. Answer based on the provided context.",
        "test_cases": TEST_CASES_D3FEND,
    }
}
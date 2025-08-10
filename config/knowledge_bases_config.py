# config/knowledge_bases_config.py

import os

# --- IMPORTAÇÃO DE TODOS OS PARSERS ---

# Parsers de Threat Intelligence
from parsers.ThreatIntel.parse_cwe_xml import parse_cwe_from_xml
from parsers.ThreatIntel.parse_capec_xml import parse_capec_from_xml
from parsers.ThreatIntel.parse_d3fend_ttl import parse_d3fend_from_ttl

# Parsers de Frameworks
from parsers.Frameworks.parse_nist_800_53b import parse_nist_sp_800_53r5
from parsers.Frameworks.parse_nist_csf2 import parse_nist_csf2
from parsers.Frameworks.parse_iso_27002 import parse_iso_27002

# ---> ADD NEW GUIDE PARSER IMPORT
#from parsers.Basics.parse_csslp_guide import parse_csslp_guide
# Parsers de Regulamentação
from parsers.Regulations.parse_gdpr import parse_gdpr_from_text
from parsers.Regulations.parse_dora import parse_dora_from_text
from parsers.Regulations.parse_nis2 import parse_nis2_from_text

# --- IMPORTAÇÃO DE TODOS OS TEST SUITES (para referência futura) ---
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

# Define o caminho base para a pasta de documentos
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')

# ==============================================================================
# NÍVEL 1: O ÍNDICE DE CATEGORIAS (para o primeiro router)
# ==============================================================================
CATEGORY_DESCRIPTIONS = {
    "Regulations": "Contains the full text of legal and regulatory mandates related to cybersecurity and data privacy. Use this for questions about legal obligations, compliance requirements, data breach notifications, and specific articles or clauses from laws like GDPR, DORA, and the NIS2 Directive.",
    "Frameworks": "Contains standards, best practices, and catalogs of security controls for managing information security. Use this for questions about implementing security programs, risk management, security controls (e.g., access control, encryption), and guidance from standards like NIST CSF, NIST 800-53, and ISO/IEC 27002.",
    "Threat Intelligence": "Contains technical catalogs of software weaknesses (CWE), common attack patterns (CAPEC), and defensive techniques (D3FEND). Use this for questions about how attacks work, specific software vulnerabilities, adversary tactics, and technical countermeasures."
}

# ==============================================================================
# NÍVEL 2: O ÍNDICE DE DOCUMENTOS (dicionário unificado)
# ==============================================================================
ALL_KNOWLEDGE_BASES = {
    # === CATEGORIA: REGULATIONS ===
    "GDPR": {
        "category": "Regulations",
        "name": "GDPR",
        "description": "A European Union regulation on data protection and privacy for all individuals within the EU. It covers principles like data minimization, consent, and rights of data subjects. It is not a technical cybersecurity standard.",
        "parser": parse_gdpr_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "GDPR.txt"),
        "collection_name": "gdpr_v1_final_modular",
        "system_prompt": "You are a legal assistant specializing in data protection. Answer questions based on the provided General Data Protection Regulation (GDPR) text.",
        "test_cases": TEST_CASES_GDPR,
    },
    "DORA": {
        "category": "Regulations",
        "name": "DORA (Digital Operational Resilience Act)",
        "description": "A European Union regulation for the financial sector focusing on digital operational resilience. It specifies requirements for ICT risk management, incident reporting, resilience testing, and third-party risk management.",
        "parser": parse_dora_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "DORA.txt"),
        "collection_name": "dora_v1_final_modular",
        "system_prompt": "You are a legal and compliance expert for the financial sector. Answer questions based on the provided Digital Operational Resilience Act (DORA) text.",
        "test_cases": TEST_CASES_DORA,
    },
    "NIS2 Directive": {
        "category": "Regulations",
        "name": "NIS2 Directive",
        "description": "A European Union directive aiming to achieve a high common level of cybersecurity across the Member States. It focuses on critical infrastructure sectors, supply chain security, and incident reporting obligations.",
        "parser": parse_nis2_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIS2.txt"),
        "collection_name": "nis2_v1_final_modular",
        "system_prompt": "You are an expert on European cybersecurity legislation. Answer questions based on the provided NIS2 Directive text.",
        "test_cases": TEST_CASES_NIS2,
    },

    # === CATEGORIA: FRAMEWORKS ===
    "NIST SP 800-53 Rev. 5": {
        "category": "Frameworks",
        "name": "NIST SP 800-53 Rev. 5",
        "description": "A comprehensive catalog of security and privacy controls for all U.S. federal information systems. It is highly detailed and organized into 20 control families (e.g., AC for Access Control, AU for Audit).",
        "parser": parse_nist_sp_800_53r5,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIST.SP.800-53r5.txt"),
        "collection_name": "nist80053r5_v1_modular",
        "system_prompt": "You are an expert in cybersecurity compliance. Answer questions about security controls based on the provided NIST SP 800-53 context.",
        "test_cases": TEST_CASES_NIST_SP_800_53R5,
    },
    "NIST CSF 2.0": {
        "category": "Frameworks",
        "name": "NIST CSF 2.0",
        "description": "A high-level, flexible framework for managing cybersecurity risk. It is organized around six core functions: Govern, Identify, Protect, Detect, Respond, and Recover. It is less prescriptive than NIST 800-53.",
        "parser": parse_nist_csf2,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NISTCSWP29.txt"),
        "collection_name": "nist_csf2_v1_modular",
        "system_prompt": "You are an expert in cybersecurity risk management. Answer questions based on the provided NIST Cybersecurity Framework (CSF) 2.0 context.",
        "test_cases": TEST_CASES_NIST_CSF2,
    },
    "ISO/IEC 27002:2022": {
        "category": "Frameworks",
        "name": "ISO/IEC 27002:2022",
        "description": "An international standard providing a detailed catalog of 93 information security controls and implementation guidance. It is often used to support an ISO 27001 certified Information Security Management System (ISMS).",
        "parser": parse_iso_27002,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "ISO_27002.txt"),
        "collection_name": "iso_27002_v1_modular",
        "system_prompt": "You are an information security specialist. Answer questions about security controls based on the provided ISO/IEC 27002:2022 context.",
        "test_cases": TEST_CASES_ISO_27002,
    },

    # === CATEGORIA: THREAT INTELLIGENCE ===
    "CWE": {
        "category": "Threat Intelligence",
        "name": "CWE (Common Weakness Enumeration)",
        "description": "A community-developed list of common software and hardware weakness types. It serves as a common language for describing security weaknesses in architecture, design, or code (e.g., CWE-79 for Cross-Site Scripting).",
        "parser": parse_cwe_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "cwec_latest.xml"),
        "collection_name": "cwe_xml_modular",
        "system_prompt": "You are a cybersecurity expert specializing in software vulnerabilities. Answer questions based on the provided CWE context.",
        "test_cases": TEST_CASES_CWE,
    },
    "CAPEC": {
        "category": "Threat Intelligence",
        "name": "CAPEC (Common Attack Pattern Enumeration and Classification)",
        "description": "A comprehensive dictionary of known patterns of attack employed by adversaries to exploit known weaknesses in cyber-enabled capabilities. It describes the 'how' of an attack.",
        "parser": parse_capec_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "capec_latest.xml"),
        "collection_name": "capec_xml_modular",
        "system_prompt": "You are a cybersecurity expert specializing in attack patterns. Answer questions based on the provided CAPEC context.",
        "test_cases": TEST_CASES_CAPEC,
    },
    "D3FEND": {
        "category": "Threat Intelligence",
        "name": "D3FEND",
        "description": "A knowledge graph of defensive cybersecurity techniques, also known as countermeasures. It provides a catalog of technologies and methods to counter specific offensive techniques.",
        "parser": parse_d3fend_from_ttl,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "d3fend.txt"),
        "collection_name": "d3fend_ontology_modular",
        "system_prompt": "You are a cybersecurity expert specialized in the D3FEND ontology, focusing on defensive cybersecurity techniques.",
        "test_cases": TEST_CASES_D3FEND,
    },
        # ---> ADD THE NEW GUIDE KNOWLEDGE BASE
    # === CATEGORIA: GUIDES ===
    #"CSSLP Guide": {
    #    "category": "Guides",
    #    "name": "CSSLP Guide",
    #    "description": "An official and comprehensive exam guide for the Certified Secure Software Lifecycle Professional (CSSLP) certification. Use this for detailed questions about secure software development, security principles, and the CSSLP domains.",
    #    "parser": parse_csslp_guide,
    #    "file_path": os.path.join(DOCS_DIRECTORY_PATH, "CSSLP Cert Guide.pdf"),
    #    "collection_name": "csslp_guide_v1_enriched",
    #    "system_prompt": "You are an expert on the CSSLP certification. Answer questions based on the provided text from the official exam guide.",
    #    "test_cases": TEST_CASES_CSSLP_GUIDE,
    #},
}
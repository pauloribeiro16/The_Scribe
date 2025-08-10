# config/sources.py
import os

# Importar os parsers
from parsers.ThreatIntel.parse_cwe_xml import parse_cwe_from_xml
from parsers.ThreatIntel.parse_capec_xml import parse_capec_from_xml
from parsers.ThreatIntel.parse_d3fend_ttl import parse_d3fend_from_ttl
from test_suites.ThreatIntel.Tests_d3fend import TEST_CASES_D3FEND # Atenção ao 'T' maiúsculo

docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
# Importar os casos de teste
from test_suites.ThreatIntel.tests_cwe import TEST_CASES_CWE
from test_suites.ThreatIntel.tests_capec import TEST_CASES_CAPEC

# Define o caminho base para a pasta de documentos
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')

# Dicionário de configuração de todas as fontes de Threat Intelligence
THREAT_INTEL_CONFIG = {
    "CWE (Common Weakness Enumeration)": {
        "parser": parse_cwe_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "cwec_latest.xml"),
        "collection_name": "cwe_xml_modular",
        "test_cases": TEST_CASES_CWE,
        "system_prompt": "You are a cybersecurity expert specializing in software vulnerabilities. Answer questions based on the provided Common Weakness Enumeration (CWE) context."
    },
    "CAPEC (Common Attack Pattern Enumeration and Classification)": {
        "parser": parse_capec_from_xml,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "capec_latest.xml"),
        "collection_name": "capec_xml_modular",
        "test_cases": TEST_CASES_CAPEC,
        "system_prompt": "You are a cybersecurity expert specializing in attack patterns. Answer questions based on the provided Common Attack Pattern Enumeration and Classification (CAPEC) context."
    },
    "D3FEND (Defensive Cybersecurity Techniques)": {
        "name": "D3FEND Ontology",
        "file_path": os.path.join(docs_path, "d3fend.txt"),
        "parser": parse_d3fend_from_ttl,
        "collection_name": "d3fend_ontology_modular",
        "test_cases": TEST_CASES_D3FEND,
        "system_prompt": "You are a cybersecurity expert specialized in the D3FEND ontology, focusing on defensive cybersecurity techniques. Answer questions using only the provided context."
    },
}
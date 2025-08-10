import os

# Importar as funções de parser
from parsers.Regulations.parse_gdpr import parse_gdpr_from_text
from parsers.Regulations.parse_dora import parse_dora_from_text
from parsers.Regulations.parse_nis2 import parse_nis2_from_text

# Importar os casos de teste
from test_suites.Regulations.tests_gdpr import TEST_CASES_GDPR
from test_suites.Regulations.tests_dora import TEST_CASES_DORA
from test_suites.Regulations.tests_nis2 import TEST_CASES_NIS2

# Define o caminho base para a pasta de documentos, relativo a este ficheiro
# 'os.path.dirname(__file__)' obtém o diretório atual (config)
# '..' sobe um nível para a pasta raiz do projeto
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')

# Dicionário de configuração de todas as fontes de dados de regulamentos
REGULATIONS_CONFIG = {
    "GDPR": {
        "parser": parse_gdpr_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "GDPR.txt"),
        "collection_name": "gdpr_v1_final_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_GDPR,
        "system_prompt": "You are a legal assistant specializing in data protection. Answer questions based on the provided General Data Protection Regulation (GDPR) text. Cite articles and recitals where possible."
    },
    "DORA": {
        "parser": parse_dora_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "DORA.txt"),
        "collection_name": "dora_v1_final_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_DORA,
        "system_prompt": "You are a legal and compliance expert for the financial sector. Answer questions based on the provided Digital Operational Resilience Act (DORA) text."
    },
    "NIS2 Directive": {
        "parser": parse_nis2_from_text,
        "file_path": os.path.join(DOCS_DIRECTORY_PATH, "NIS2.txt"),
        "collection_name": "nis2_v1_final_modular", # <-- CORRIGIDO
        "test_cases": TEST_CASES_NIS2,
        "system_prompt": "You are an expert on European cybersecurity legislation. Answer questions based on the provided NIS2 Directive text."
    },
    # Para adicionar um novo regulamento, basta adicionar uma nova entrada aqui
}
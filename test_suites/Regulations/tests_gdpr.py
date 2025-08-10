# test_suites/tests_gdpr.py

# O nome da variável deve ser único para evitar conflitos quando for importado.
# Uma boa convenção é TEST_CASES_<NOME_DO_REGULAMENTO>.
TEST_CASES_GDPR = [
    { 
        "category": "Core Definitions", 
        "question": "What is the definition of 'personal data' specified in GDPR?",
        "golden_answer": "Personal data is any information that relates to an identified or identifiable living individual. This includes obvious identifiers like a name or an ID number, as well as other data like location, IP address, or biometric data that can be used to identify a person. (Reference: Article 4(1))" 
    },
    {
        "category": "Data Subject Rights",
        "question": "Under what conditions can a person request their data to be erased, according to Article 17?",
        "golden_answer": "A person can request erasure if the data is no longer necessary, if they withdraw consent, if they object to processing and there are no overriding legitimate grounds, if the data was unlawfully processed, if erasure is required for legal compliance, or if the data was collected in relation to information society services offered to a child. (Reference: Article 17(1))"
    }
    # ... pode adicionar mais casos de teste para o GDPR aqui ...
]
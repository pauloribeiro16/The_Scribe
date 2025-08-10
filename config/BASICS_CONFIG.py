import os
from parsers.Basics.parse_csslp_guide import parse_csslp_guide
#Define the base path to the documents folder
DOCS_DIRECTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs')
BASICS_CONFIG = {
    "CSSLP Guide": {
    "name": "CSSLP Guide",
    "parser": parse_csslp_guide,
    "file_path": os.path.join(DOCS_DIRECTORY_PATH, "CSSLP Cert Guide.pdf"), # The name of your PDF
    "collection_name": "csslp_guide_v1_enriched", # A unique name for the Qdrant collection
    "description": "An official and comprehensive exam guide for the Certified Secure Software Lifecycle Professional (CSSLP) certification. Use this for detailed questions about secure software development, security principles, and the CSSLP domains.",
    # The test_cases and system_prompt keys can be added here if needed, following your existing pattern
    "test_cases": [],
    "system_prompt": "You are an expert on the CSSLP certification. Answer questions based on the provided text from the official exam guide."
    },
    # You can add other guides here in the future
}
# parsers/Frameworks/parse_nist_csf2.py

import os
import re
import logging
from typing import List
from llama_index.core import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_nist_csf2(file_path: str) -> List[Document]:
    """
    Parses the NIST CSF 2.0 text file, creating a granular Document for each
    individual Control Subcategory (e.g., ID.AM-01).
    """
    logging.info(f"Starting granular parsing of NIST CSF 2.0 file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except Exception as e:
        logging.error(f"Failed to read file: {e}")
        return []

    llama_documents = []
    source_filename = os.path.basename(file_path)

    # Isolate the main content of the Core from Appendix A to Appendix B
    try:
        core_content = re.search(r'Appendix A\. The CSF Core([\s\S]+?)Appendix B\. CSF Tiers', full_text, re.DOTALL).group(1)
    except AttributeError:
        logging.error("Could not isolate the CSF Core content (Appendix A to B). Check document markers.")
        return []
    
    # Regex to find each subcategory block. It looks for the ID and captures everything until the next ID.
    subcategory_pattern = r'((GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2})([\s\S]+?)(?=(?:GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}|\Z)'
    
    # Pre-process to find all function and category titles for context
    functions = dict(re.findall(r'([A-Z]{6,})\s\(([A-Z]{2})\):', core_content))
    categories = dict(re.findall(r'([A-Za-z\s]+)\s\((GV|ID|PR|DE|RS|RC)\.[A-Z]{2}\):', core_content))

    for match in re.finditer(subcategory_pattern, core_content, re.DOTALL):
        subcategory_id = match.group(1)
        subcategory_text = match.group(3).strip()
        
        # Extract the title of the subcategory (the first line of its text)
        subcategory_title = subcategory_text.split('\n')[0].strip()
        
        # Determine parent Function and Category from the ID
        function_id = subcategory_id.split('.')[0]
        category_id = ".".join(subcategory_id.split('-')[0].split('.')[:2])
        
        function_name = functions.get(function_id, "Unknown Function")
        category_name = "Unknown Category"
        for title, cat_id in categories.items():
            if cat_id == category_id:
                category_name = title
                break

        # Text Enrichment
        enriched_text = (
            f"From NIST CSF 2.0:\n"
            f"Function: {function_name} ({function_id})\n"
            f"Category: {category_name} ({category_id})\n"
            f"Subcategory: {subcategory_title} ({subcategory_id})\n\n"
            f"### Implementation Examples\n{subcategory_text}"
        )

        # Metadata Enrichment
        metadata = {
            "source_document": "NIST CSF 2.0",
            "function_id": function_id,
            "function_name": function_name,
            "category_id": category_id,
            "category_name": category_name,
            "subcategory_id": subcategory_id,
            "subcategory_title": subcategory_title,
        }
        
        llama_documents.append(Document(text=enriched_text, metadata=metadata))

    logging.info(f"Granular parsing of NIST CSF 2.0 complete. {len(llama_documents)} documents (subcategories) created.")
    return llama_documents
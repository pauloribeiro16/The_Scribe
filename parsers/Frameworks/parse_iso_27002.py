# parsers/Frameworks/parse_iso_27002.py

import os
import re
import logging
from typing import List
from llama_index.core import Document

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_iso_27002(file_path: str) -> List[Document]:
    """
    Parses the full text of ISO/IEC 27002:2022 using the validated and robust
    parsing logic. It creates a self-contained and enriched Document for each control.
    """
    logging.info(f"Starting robust parsing of ISO/IEC 27002:2022 file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"ISO 27002 text file not found at: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except IOError as e:
        logging.error(f"Failed to read text file {file_path}: {e}")
        return []

    llama_documents = []
    source_filename = os.path.basename(file_path)

    # --- Isolate the main controls section (Clauses 5-8) using the proven regex ---
    try:
        main_content_match = re.search(r'5\s+Organizational controls\s*\n\s*5\.1([\s\S]+?)Annex A', full_text, re.DOTALL)
        if not main_content_match:
            logging.error("Could not isolate the content of Clauses 5-8. Please check the document markers.")
            return []
        # Add the start of the first control back to be included in the parsing loop
        main_content = "5.1" + main_content_match.group(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while extracting the main content: {e}")
        return []

    themes = {
        '5': 'Organizational controls',
        '6': 'People controls',
        '7': 'Physical controls',
        '8': 'Technological controls',
    }

    # Pattern to find each individual control block.
    control_pattern = r'(\d{1,2}\.\d{1,2}\s+[A-Za-z][\s\S]+?)(?=\n\d{1,2}\.\d{1,2}\s+[A-Za-z]|\Z)'

    for match in re.finditer(control_pattern, main_content, re.DOTALL):
        block = match.group(1).strip()
        
        header_match = re.search(r'^(\d{1,2}\.\d{1,2})\s+([^\n]+)', block)
        if not header_match:
            continue
            
        control_id = header_match.group(1).strip()
        control_title = header_match.group(2).strip()
        
        clause_num = control_id.split('.')[0]
        current_theme = themes.get(clause_num, "Unknown")

        # Safely parse each section to prevent errors
        control_text_match = re.search(r'Control\n([\s\S]+?)(?=\n\s*Purpose\n|$)', block, re.DOTALL)
        control_text = ' '.join(control_text_match.group(1).strip().split()) if control_text_match else "Not specified."
        
        purpose_text_match = re.search(r'Purpose\n([\s\S]+?)(?=\n\s*Guidance\n|$)', block, re.DOTALL)
        purpose_text = ' '.join(purpose_text_match.group(1).strip().split()) if purpose_text_match else "Not specified."
        
        guidance_text = ""
        other_info_text = ""
        guidance_part_match = re.search(r'Guidance\n([\s\S]*)', block, re.DOTALL)
        if guidance_part_match:
            guidance_part = guidance_part_match.group(1).strip()
            if '\nOther information\n' in guidance_part:
                parts = guidance_part.split('\nOther information\n', 1)
                guidance_text = ' '.join(parts[0].strip().split())
                other_info_text = ' '.join(parts[1].strip().split())
            else:
                guidance_text = ' '.join(guidance_part.strip().split())
        
        attribute_region_match = re.search(r'Control type([\s\S]+?)Control\n', block, re.DOTALL)
        attributes = sorted(list(set(re.findall(r'(#[\w_]+)', attribute_region_match.group(1))))) if attribute_region_match else []

        metadata = {
            "source_document": "ISO/IEC 27002:2022",
            "control_theme": current_theme,
            "control_id": control_id,
            "control_title": control_title,
            "attributes": attributes
        }

        # Apply the "Enriched Chunk" principle for clear context
        enriched_text = (
            f"From ISO/IEC 27002:2022:\n"
            f"### Control {control_id}: {control_title}\n\n"
            f"**Attributes:** {', '.join(attributes)}\n\n"
            f"**Control Statement:**\n{control_text}\n\n"
            f"**Purpose:**\n{purpose_text}\n\n"
            f"**Guidance:**\n{guidance_text}\n\n"
            f"**Other Information:**\n{other_info_text}"
        ).strip()
        
        doc = Document(text=enriched_text, metadata=metadata)
        llama_documents.append(doc)
        
    logging.info(f"Parsing complete. Successfully created {len(llama_documents)} document chunks.")
    return llama_documents
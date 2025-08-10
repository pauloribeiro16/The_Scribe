import os
import re
import logging
from typing import List, Set
from llama_index.core import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _clean_text_block(text: str) -> str:
    if not text: return ""
    text = re.sub(r'CHAPTER THREE.*?_{2,}', '', text, flags=re.DOTALL)
    text = re.sub(r'NIST SP 800-53, REV\. 5.*?ORGANIZATIONS', '', text, flags=re.DOTALL)
    text = ' '.join(text.strip().split())
    return text

def parse_nist_sp_800_53r5(file_path: str) -> List[Document]:
    """
    Parses the NIST SP 800-53 Rev. 5 text file, creating an enriched and
    self-contained Document for each control and enhancement.
    """
    logging.info(f"Parsing NIST SP 800-53 Rev. 5 with text enrichment: {file_path}")
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
    
    try:
        chapter_3_text = re.search(r'CHAPTER THREE\s*\n\s*THE CONTROLS([\s\S]+?)APPENDIX A', full_text, re.DOTALL).group(1)
    except AttributeError:
        logging.error("Could not isolate Chapter 3. Check document markers.")
        return []
    
    anchor_pattern = re.compile(r'^(?:([A-Z]{2}-\d+)\s+([A-Z\s-]+)|(\(\d+\))\s+([A-Z\s\(\)–-]+))$', re.MULTILINE)
    matches = list(anchor_pattern.finditer(chapter_3_text))

    if not matches: return []

    parent_control_id = None
    parent_control_name = None

    for i, match in enumerate(matches):
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(chapter_3_text)
        block_text = chapter_3_text[start_pos:end_pos]

        control_id, control_name, enhancement_num, enhancement_name = match.groups()

        if control_id:
            parent_control_id = control_id.strip()
            parent_control_name = control_name.strip()
            content_text = block_text.split("Control Enhancements:", 1)[0]
            
            ##### START OF FIX #####
            # Check if the regex finds a match before trying to access group(1).
            statement_match = re.search(r'Control:\s*([\s\S]+?)(?:Discussion:|$)', content_text, re.DOTALL)
            statement = _clean_text_block(statement_match.group(1)) if statement_match else ""
            
            discussion_match = re.search(r'Discussion:\s*([\s\S]+)', content_text, re.DOTALL)
            discussion = _clean_text_block(discussion_match.group(1)) if discussion_match else ""
            ##### END OF FIX #####

            enriched_text = (
                f"From NIST SP 800-53 Rev. 5:\n"
                f"### Base Control: {parent_control_id} ({parent_control_name})\n\n"
                f"**Control Statement:** {statement}\n\n"
                f"**Discussion:** {discussion}"
            ).strip()
            
            metadata = {
                "source_document": "NIST SP 800-53",
                "control_family": parent_control_id.split('-')[0],
                "control_id": parent_control_id,
                "control_name": parent_control_name,
                "type": "Base Control"
            }
            llama_documents.append(Document(text=enriched_text, metadata=metadata))

        elif enhancement_num and parent_control_id:
            enhancement_id = f"{parent_control_id}{enhancement_num.strip()}"
            enhancement_name = enhancement_name.strip()
            
            # The enhancement text is the whole block minus the title line
            statement = _clean_text_block(block_text.replace(match.group(0), ''))

            enriched_text = (
                f"From NIST SP 800-53 Rev. 5:\n"
                f"### Control Enhancement: {enhancement_id} ({enhancement_name})\n\n"
                f"**Parent Control:** {parent_control_id} ({parent_control_name})\n\n"
                f"**Enhancement Statement:** {statement}"
            ).strip()

            metadata = {
                "source_document": "NIST SP 800-53",
                "control_family": parent_control_id.split('-')[0],
                "control_id": enhancement_id,
                "control_name": enhancement_name,
                "type": "Control Enhancement"
            }
            llama_documents.append(Document(text=enriched_text, metadata=metadata))

    logging.info(f"Parsing of NIST 800-53 complete. {len(llama_documents)} documents created.")
    return llama_documents
import os
import logging
import xml.etree.ElementTree as ET
from typing import List
from llama_index.core import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NAMESPACES = {
    'capec': 'http://capec.mitre.org/capec-3',
    'xhtml': 'http://www.w3.org/1999/xhtml'
}

# The helper functions (_get_complex_text, etc.) can be shared or redefined here.
# For simplicity, we'll redefine the necessary ones.

def _get_complex_text(element: ET.Element, tag: str) -> str:
    node = element.find(f'capec:{tag}', NAMESPACES)
    if node is None: return ""
    parts = []
    for child in node:
        if child.tag == f"{{{NAMESPACES['xhtml']}}}p":
            parts.append("".join(child.itertext()).strip())
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}ul":
            list_items = [f"* {''.join(li.itertext()).strip()}" for li in child.findall(f".//xhtml:li", NAMESPACES)]
            parts.append("\n".join(list_items))
    if not parts: return ' '.join(''.join(node.itertext()).strip().split())
    return "\n\n".join(filter(None, parts))

def _format_related_attack_patterns(element: ET.Element) -> str:
    container = element.find('capec:Related_Attack_Patterns', NAMESPACES)
    if container is None: return ""
    relations = [f"* {p.get('Nature')}: CAPEC-{p.get('CAPEC_ID')}" for p in container.findall('capec:Related_Attack_Pattern', NAMESPACES)]
    return "\n".join(relations)

def _format_consequences(element: ET.Element) -> str:
    container = element.find('capec:Consequences', NAMESPACES)
    if container is None: return ""
    consequences = []
    for cons in container.findall('capec:Consequence', NAMESPACES):
        scopes = ", ".join([s.text for s in cons.findall('capec:Scope', NAMESPACES)])
        impacts = ", ".join([i.text for i in cons.findall('capec:Impact', NAMESPACES)])
        consequences.append(f"* **Scope(s)**: {scopes} | **Impact(s)**: {impacts}")
    return "\n".join(consequences)


def parse_capec_from_xml(file_path: str) -> List[Document]:
    """
    Parses the CAPEC XML file into granular, self-contained, and enriched Documents.
    """
    logging.info(f"Starting granular parsing of CAPEC XML file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"CAPEC XML file not found at: {file_path}")
        return []

    try:
        ET.register_namespace('capec', NAMESPACES['capec'])
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML file {file_path}: {e}")
        return []

    all_documents = []
    attack_patterns = root.findall('.//capec:Attack_Pattern', NAMESPACES)

    for pattern in attack_patterns:
        if pattern.get('Status') == 'Deprecated':
            continue

        capec_id = pattern.get('ID')
        name = pattern.get('Name', 'N/A')
        
        related_cwe_ids = [f"CWE-{node.get('CWE_ID')}" for node in pattern.findall('.//capec:Related_Weakness', NAMESPACES) if node.get('CWE_ID')]

        base_metadata = {
            "source_document": "CAPEC",
            "capec_id": f"CAPEC-{capec_id}",
            "name": name,
            "abstraction": pattern.get('Abstraction', 'N/A'),
            "status": pattern.get('Status', 'N/A'),
            "related_cwe_ids": related_cwe_ids
        }

        # Define sections to be parsed into individual documents
        sections_to_parse = {
            "Description": _get_complex_text(pattern, 'Description'),
            "Execution Flow": _get_complex_text(pattern, 'Execution_Flow'), # Simplified for brevity
            "Mitigations": _get_complex_text(pattern, 'Mitigations'),
            "Consequences": _format_consequences(pattern),
            "Related Attack Patterns": _format_related_attack_patterns(pattern),
        }

        for section_title, section_content in sections_to_parse.items():
            if section_content and section_content != "N/A":
                enriched_text = f"From {base_metadata['capec_id']} ({base_metadata['name']}):\n### {section_title}\n\n{section_content}"
                metadata = base_metadata.copy()
                metadata["section"] = section_title
                doc = Document(text=enriched_text, metadata=metadata)
                all_documents.append(doc)
    
    logging.info(f"Granular parsing complete. {len(all_documents)} CAPEC documents created.")
    return all_documents
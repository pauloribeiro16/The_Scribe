import os
import logging
import xml.etree.ElementTree as ET
from typing import List
from llama_index.core import Document

##### NEW/CHANGED SECTION - HELPER FUNCTIONS ARE NOW MORE MODULAR #####
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NAMESPACES = {
    'cwe': 'http://cwe.mitre.org/cwe-7',
    'xhtml': 'http://www.w3.org/1999/xhtml'
}

def _get_complex_text(element: ET.Element, tag: str) -> str:
    # This helper function is largely the same but crucial for the new structure.
    # It extracts and formats text from complex nodes.
    node = element.find(f'cwe:{tag}', NAMESPACES)
    if node is None:
        return ""
    
    parts = []
    for child in node:
        if child.tag == f"{{{NAMESPACES['xhtml']}}}p":
            parts.append("".join(child.itertext()).strip())
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}ul":
            list_items = [f"* {''.join(li.itertext()).strip()}" for li in child.findall(f".//xhtml:li", NAMESPACES)]
            parts.append("\n".join(list_items))
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}div":
            parts.append(f"```\n{''.join(child.itertext()).strip()}\n```")

    if not parts:
        return ' '.join(''.join(node.itertext()).strip().split())
        
    return "\n\n".join(filter(None, parts))

def _format_structured_list(element: ET.Element, path: str, item_tag: str, fields: dict) -> str:
    # This helper function is also similar but vital.
    container = element.find(f'cwe:{path}', NAMESPACES)
    if container is None: return ""
    
    items_text = []
    for item in container.findall(f'cwe:{item_tag}', NAMESPACES):
        item_parts = []
        for field_name, tag_name in fields.items():
            values = [n.text.strip() for n in item.findall(f'cwe:{tag_name}', NAMESPACES) if n.text]
            if values: item_parts.append(f"**{field_name}**: {', '.join(values)}")
        
        note_node = item.find('cwe:Note', NAMESPACES) or item.find('cwe:Description', NAMESPACES)
        if note_node is not None:
             item_parts.append(_get_complex_text(item, note_node.tag.split('}')[-1]))

        if item_parts: items_text.append("* " + "\n  ".join(item_parts))
    return "\n\n".join(items_text)

def _format_demonstrative_examples(element: ET.Element, parent_metadata: dict) -> List[Document]:
    # This function now returns a list of Document objects, one for each example.
    examples_node = element.find('cwe:Demonstrative_Examples', NAMESPACES)
    if examples_node is None: return []

    example_docs = []
    for i, example in enumerate(examples_node.findall('cwe:Demonstrative_Example', NAMESPACES)):
        example_id = i + 1
        example_parts = []
        intro = _get_complex_text(example, 'Intro_Text')
        if intro: example_parts.append(intro)
        
        for code_node in example.findall('cwe:Example_Code', NAMESPACES):
            nature = code_node.get('Nature', 'Code')
            lang = code_node.get('Language', '')
            code_text = ''.join(code_node.itertext()).strip()
            example_parts.append(f"**Nature**: {nature}\n```{lang}\n{code_text}\n```")
            
        body = _get_complex_text(example, 'Body_Text')
        if body: example_parts.append(body)

        if not example_parts: continue

        section_content = "\n\n".join(example_parts)
        # Text Enrichment
        enriched_text = f"From {parent_metadata['cwe_id']} ({parent_metadata['cwe_name']}):\n### Demonstrative Example {example_id}\n\n{section_content}"
        
        # Metadata Enrichment
        metadata = parent_metadata.copy()
        metadata["section"] = f"Demonstrative Example {example_id}"
        
        example_docs.append(Document(text=enriched_text, metadata=metadata))
        
    return example_docs

##### END OF NEW/CHANGED SECTION #####


def parse_cwe_from_xml(file_path: str) -> List[Document]:
    """
    Parses the CWE XML file into granular, self-contained, and enriched Documents.
    Each logical section of a CWE entry (Description, Mitigations, etc.) becomes a separate Document.
    """
    logging.info(f"Starting granular parsing of CWE XML file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"CWE XML file not found at: {file_path}")
        return []

    try:
        ET.register_namespace('cwe', NAMESPACES['cwe'])
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML file {file_path}: {e}")
        return []

    all_documents = []
    source_filename = os.path.basename(file_path)
    
    weaknesses = root.find('cwe:Weaknesses', NAMESPACES)
    if weaknesses is None: return []

    for weakness in weaknesses.findall('cwe:Weakness', NAMESPACES):
        cwe_id = weakness.get('ID')
        cwe_name = weakness.get('Name', 'N/A')
        
        related_capec_ids = [node.get('CAPEC_ID') for node in weakness.findall('.//cwe:Related_Attack_Pattern', NAMESPACES) if node.get('CAPEC_ID')]

        # Base metadata for all chunks related to this CWE
        base_metadata = {
            "source_document": "CWE",
            "cwe_id": f"CWE-{cwe_id}",
            "cwe_name": cwe_name,
            "abstraction": weakness.get('Abstraction', 'N/A'),
            "status": weakness.get('Status', 'N/A'),
            "related_capec_ids": [f"CAPEC-{cid}" for cid in related_capec_ids]
        }

        # Define sections to be parsed into individual documents
        sections_to_parse = {
            "Description": _get_complex_text(weakness, 'Description'),
            "Extended Description": _get_complex_text(weakness, 'Extended_Description'),
            "Potential Mitigations": _get_complex_text(weakness, 'Potential_Mitigations'),
            "Common Consequences": _format_structured_list(weakness, 'Common_Consequences', 'Consequence', {'Scope': 'Scope', 'Impact': 'Impact'}),
            "Detection Methods": _format_structured_list(weakness, 'Detection_Methods', 'Detection_Method', {'Method': 'Method', 'Effectiveness': 'Effectiveness'}),
        }
        
        # Create a document for each standard text section
        for section_title, section_content in sections_to_parse.items():
            if section_content and section_content != "N/A":
                # Text Enrichment
                enriched_text = f"From {base_metadata['cwe_id']} ({base_metadata['cwe_name']}):\n### {section_title}\n\n{section_content}"
                
                # Metadata Enrichment
                metadata = base_metadata.copy()
                metadata["section"] = section_title
                
                doc = Document(text=enriched_text, metadata=metadata)
                all_documents.append(doc)

        # Create separate documents for each demonstrative example
        example_docs = _format_demonstrative_examples(weakness, base_metadata)
        all_documents.extend(example_docs)

    logging.info(f"Granular parsing complete. {len(all_documents)} CWE documents created.")
    return all_documents
import os
import logging
import xml.etree.ElementTree as ET
from typing import List
from llama_index.core import Document

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Parsing Logic (Self-contained and Updated) ---

# Namespaces are crucial for finding any element in the CAPEC XML.
NAMESPACES = {
    'capec': 'http://capec.mitre.org/capec-3',
    'xhtml': 'http://www.w3.org/1999/xhtml'
}

def get_text_from_element(element: ET.Element, path: str, default: str = "") -> str:
    """Extracts text from a simple element, handling namespaces."""
    node = element.find(path, NAMESPACES)
    if node is not None and node.text:
        return node.text.strip()
    return default

def get_complex_text_content(element: ET.Element, tag: str) -> str:
    """Extracts and formats text from elements that contain nested XHTML tags."""
    node = element.find(f'capec:{tag}', NAMESPACES)
    if node is None:
        return ""
    
    parts = []
    # Using iter() to process all sub-elements in document order
    for child in node:
        if child.tag == f"{{{NAMESPACES['xhtml']}}}p":
            text = "".join(child.itertext()).strip()
            if text:
                parts.append(text)
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}ul":
            list_items = [f"* {''.join(li.itertext()).strip()}" for li in child.findall(".//xhtml:li", NAMESPACES) if ''.join(li.itertext()).strip()]
            if list_items:
                parts.append("\n".join(list_items))
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}div":
            text = "".join(child.itertext()).strip()
            if text:
                parts.append(f"```\n{text}\n```")

    # Fallback if no structured xhtml tags were found, but the main node has text
    if not parts:
        full_text = ' '.join(''.join(node.itertext()).strip().split())
        return full_text if full_text else ""
        
    return "\n\n".join(parts)

def format_alternate_terms(element: ET.Element) -> str:
    """Formats the 'Alternate_Terms' section into a Markdown list."""
    container = element.find('capec:Alternate_Terms', NAMESPACES)
    if container is None:
        return ""
    terms = [f"* {term.text.strip()}" for term in container.findall('capec:Alternate_Term/capec:Term', NAMESPACES) if term.text]
    return "\n".join(terms)

def format_related_attack_patterns(element: ET.Element) -> str:
    """Formats the 'Related_Attack_Patterns' section."""
    container = element.find('capec:Related_Attack_Patterns', NAMESPACES)
    if container is None:
        return ""
    
    relations = [
        f"* {pattern.get('Nature')}: CAPEC-{pattern.get('CAPEC_ID')}"
        for pattern in container.findall('capec:Related_Attack_Pattern', NAMESPACES)
    ]
    return "\n".join(relations)

def format_example_instances(element: ET.Element) -> str:
    """Formats the 'Example_Instances' section, handling complex content."""
    container = element.find('capec:Example_Instances', NAMESPACES)
    if container is None:
        return ""

    examples = []
    for i, example_node in enumerate(container.findall('capec:Example', NAMESPACES)):
        example_header = f"#### Example {i+1}"
        # An example node can have complex XHTML content directly
        example_content = get_complex_text_content(container, 'Example')
        examples.append(f"{example_header}\n{example_content}")

    return "\n---\n".join(examples)

def format_execution_flow(element: ET.Element) -> str:
    """Formats the 'Execution_Flow' section in a structured way (in English)."""
    flow = element.find('capec:Execution_Flow', NAMESPACES)
    if flow is None: return ""
        
    steps_text = []
    for step_node in flow.findall('capec:Attack_Step', NAMESPACES):
        step = get_text_from_element(step_node, 'capec:Step')
        phase = get_text_from_element(step_node, 'capec:Phase')
        desc = get_complex_text_content(step_node, 'Description')
        
        step_header = f"#### Step {step} (Phase: {phase})"
        steps_text.append(step_header)
        if desc:
            steps_text.append(desc)
            
        techniques = [f"  - {tech.text.strip()}" for tech in step_node.findall('capec:Technique', NAMESPACES) if tech.text]
        if techniques:
            steps_text.append("**Techniques:**\n" + "\n".join(techniques))
    
    return "\n\n".join(steps_text)

def format_consequences(element: ET.Element) -> str:
    """Formats the 'Consequences' section (in English)."""
    consequences_node = element.find('capec:Consequences', NAMESPACES)
    if consequences_node is None: return ""
        
    consequences_list = []
    for cons in consequences_node.findall('capec:Consequence', NAMESPACES):
        scopes = ", ".join([scope.text for scope in cons.findall('capec:Scope', NAMESPACES)])
        impacts = ", ".join([impact.text for impact in cons.findall('capec:Impact', NAMESPACES)])
        note = get_text_from_element(cons, 'capec:Note', default="")

        item_str = f"**Scope(s)**: {scopes} | **Impact(s)**: {impacts}"
        if note:
            item_str += f"\n  - *Note*: {note}"
        consequences_list.append(f"* {item_str}")
        
    return "\n".join(consequences_list)

def format_simple_list(element: ET.Element, path: str, item_tag: str) -> str:
    """Formats a simple list of elements (e.g., Prerequisites) in Markdown."""
    container = element.find(path, NAMESPACES)
    if container is None:
        return ""
    
    items = [f"* {item.text.strip()}" for item in container.findall(item_tag, NAMESPACES) if item.text]
    return "\n".join(items)

def parse_capec_from_xml(file_path: str) -> List[Document]:
    """Parses a CAPEC XML file and transforms each <Attack_Pattern> into a Document object."""
    logging.info(f"Starting parsing of CAPEC XML file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        for prefix, uri in NAMESPACES.items():
            ET.register_namespace(prefix, uri)
            
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logging.error(f"XML parsing error in {file_path}: {e}")
        return []

    llama_documents = []
    source_filename = os.path.basename(file_path)
    
    attack_patterns = root.findall('.//capec:Attack_Pattern', NAMESPACES)

    for pattern in attack_patterns:
        if pattern.get('Status') == 'Deprecated':
            continue

        capec_id = pattern.get('ID')
        name = pattern.get('Name', 'N/A')
        
        related_cwe_ids = [
            f"CWE-{node.get('CWE_ID')}" 
            for node in pattern.findall('.//capec:Related_Weakness', NAMESPACES) 
            if node.get('CWE_ID')
        ]

        metadata = {
            "source_file": source_filename,
            "capec_id": f"CAPEC-{capec_id}",
            "name": name,
            "abstraction": pattern.get('Abstraction', 'N/A'),
            "status": pattern.get('Status', 'N/A'),
            "related_cwe_ids": related_cwe_ids
        }

        # Build the text content in Markdown format with English headers
        text_parts = {
            "Alternate Terms": format_alternate_terms(pattern),
            "Description": get_complex_text_content(pattern, 'Description'),
            "Extended Description": get_complex_text_content(pattern, 'Extended_Description'),
            "Likelihood of Attack": get_text_from_element(pattern, 'capec:Likelihood_Of_Attack'),
            "Typical Severity": get_text_from_element(pattern, 'capec:Typical_Severity'),
            "Related Attack Patterns": format_related_attack_patterns(pattern),
            "Execution Flow": format_execution_flow(pattern),
            "Prerequisites": format_simple_list(pattern, 'capec:Prerequisites', 'capec:Prerequisite'),
            "Skills Required": get_complex_text_content(pattern, 'Skills_Required'),
            "Consequences": format_consequences(pattern),
            "Mitigations": get_complex_text_content(pattern, 'Mitigations'),
            "Example Instances": format_example_instances(pattern),
            "Related Weaknesses (CWE)": ", ".join(related_cwe_ids) or "None"
        }
        
        full_text_for_embedding = f"# {metadata['capec_id']}: {name}\n"
        full_text_for_embedding += f"**Abstraction**: {metadata['abstraction']} | **Status**: {metadata['status']}\n\n"
        
        for title, content in text_parts.items():
            if content and content != "N/A":
                full_text_for_embedding += f"### {title}\n{content}\n\n"
        
        doc = Document(text=full_text_for_embedding.strip(), metadata=metadata)
        llama_documents.append(doc)

    logging.info(f"Parsing complete. {len(llama_documents)} CAPEC attack patterns processed.")
    return llama_documents

# --- Main Test Execution Block ---
if __name__ == "__main__":
    CAPEC_FILE_PATH = 'C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\capec_latest.xml'

    parsed_documents = parse_capec_from_xml(CAPEC_FILE_PATH)
    
    if parsed_documents:
        print(f"\n✅ Parsing successful. Inspecting {len(parsed_documents)} generated document(s):\n")
        
        for i, doc in enumerate(parsed_documents):
            print(f"========================= DOCUMENT {i+1} ({doc.metadata.get('capec_id', 'N/A')}) =========================")
            
            print("\n--- EXTRACTED METADATA ---\n")
            print(doc.metadata)
            
            print("\n\n--- FULL TEXT TO BE EMBEDDED (MARKDOWN FORMAT) ---\n")
            print(doc.text)
            
            print(f"======================= END OF DOCUMENT {i+1} ========================\n\n")
    else:
        print("\n❌ No documents were generated. Please check logs and input file.")
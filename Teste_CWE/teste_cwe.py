import os
import logging
import xml.etree.ElementTree as ET
from typing import List
from llama_index.core import Document

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Parsing Logic (Self-contained) ---

NAMESPACES = {
    'cwe': 'http://cwe.mitre.org/cwe-7',
    'xhtml': 'http://www.w3.org/1999/xhtml'
}

def get_formatted_complex_text(element: ET.Element, tag: str) -> str:
    """
    Extracts text from complex nodes that may contain XHTML tags,
    preserving paragraph, list, and code block structures in Markdown.
    """
    container_node = element.find(f'cwe:{tag}', NAMESPACES)
    if container_node is None:
        return ""

    parts = []
    for child in container_node:
        if child.tag == f"{{{NAMESPACES['xhtml']}}}p":
            paragraph_text = "".join(child.itertext()).strip()
            if paragraph_text:
                parts.append(paragraph_text)
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}ul":
            list_items = []
            for li in child.findall(f"xhtml:li", NAMESPACES):
                item_text = "".join(li.itertext()).strip()
                if item_text:
                    list_items.append(f"* {item_text}")
            if list_items:
                parts.append("\n".join(list_items))
        elif child.tag == f"{{{NAMESPACES['xhtml']}}}div":
            code_text = ''.join(child.itertext()).strip()
            if code_text:
                parts.append(f"```\n{code_text}\n```")
    
    if not parts:
        full_text = ' '.join(''.join(container_node.itertext()).strip().split())
        return full_text if full_text else ""

    return "\n\n".join(filter(None, parts))

def format_structured_list(element: ET.Element, path: str, item_tag: str, fields: dict) -> str:
    """Formats a list of structured items (e.g., Consequences) into Markdown."""
    container = element.find(f'cwe:{path}', NAMESPACES)
    if container is None:
        return ""
    
    items_text = []
    for item in container.findall(f'cwe:{item_tag}', NAMESPACES):
        item_parts = []
        for field_name, tag_name in fields.items():
            nodes = item.findall(f'cwe:{tag_name}', NAMESPACES)
            if nodes:
                values = [n.text.strip() for n in nodes if n.text]
                if values:
                    item_parts.append(f"**{field_name}**: {', '.join(values)}")
        
        note_or_desc_tag = 'Note' if item.find('cwe:Note', NAMESPACES) is not None else 'Description'
        complex_content = get_formatted_complex_text(item, note_or_desc_tag)
        if complex_content:
             item_parts.append(complex_content)

        if item_parts:
            items_text.append("* " + "\n  ".join(item_parts))

    return "\n\n".join(items_text) if items_text else ""

def format_demonstrative_examples(element: ET.Element) -> str:
    """Formats Demonstrative Examples into distinct Markdown sections."""
    examples_node = element.find('cwe:Demonstrative_Examples', NAMESPACES)
    if examples_node is None:
        return ""

    examples_text = []
    for i, example in enumerate(examples_node.findall('cwe:Demonstrative_Example', NAMESPACES)):
        example_parts = [f"#### Demonstrative Example {i+1}"]
        
        intro = get_formatted_complex_text(example, 'Intro_Text')
        if intro: example_parts.append(intro)
        
        for child in example:
             if child.tag == f"{{{NAMESPACES['cwe']}}}Body_Text":
                  body_text = "".join(child.itertext()).strip()
                  if body_text:
                       example_parts.append(body_text)
             elif child.tag == f"{{{NAMESPACES['cwe']}}}Example_Code":
                  nature = child.get('Nature', 'Code')
                  lang = child.get('Language', '')
                  code_text = ''.join(child.itertext())
                  example_parts.append(f"**Code Type ({nature})**:\n```{lang}\n{code_text.strip()}\n```")
            
        examples_text.append("\n\n".join(example_parts))

    return "\n---\n".join(examples_text) if examples_text else ""

def parse_cwe_from_xml(file_path: str) -> List[Document]:
    """
    Parses a CWE XML file (full or fragment) and transforms each <Weakness> 
    into a Document object.
    """
    logging.info(f"Starting parsing of CWE XML file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return []

    try:
        ET.register_namespace('cwe', NAMESPACES['cwe'])
        ET.register_namespace('xhtml', NAMESPACES['xhtml'])

        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        
        if first_line.startswith('<?xml'):
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            wrapped_xml_content = f"<root>{xml_content}</root>"
            root = ET.fromstring(wrapped_xml_content)

    except ET.ParseError as e:
        logging.error(f"XML parsing error in {file_path}: {e}")
        return []

    llama_documents = []
    source_filename = os.path.basename(file_path)
    
    weaknesses = root.findall('.//cwe:Weakness', NAMESPACES)
    if not weaknesses:
         logging.warning("No <Weakness> elements found in the file.")
         return []

    for weakness in weaknesses:
        cwe_id = weakness.get('ID')
        cwe_name = weakness.get('Name', 'N/A')
        
        related_capecs = weakness.findall('.//cwe:Related_Attack_Pattern', NAMESPACES)
        related_capec_ids = [node.get('CAPEC_ID') for node in related_capecs if node.get('CAPEC_ID')]

        metadata = {
            "source_file": source_filename,
            "cwe_id": f"CWE-{cwe_id}",
            "cwe_name": cwe_name,
            "abstraction": weakness.get('Abstraction', 'N/A'),
            "status": weakness.get('Status', 'N/A'),
            "related_capec_ids": [f"CAPEC-{cid}" for cid in related_capec_ids] if related_capec_ids else []
        }

        related_weaknesses_nodes = weakness.findall('.//cwe:Related_Weakness', NAMESPACES)
        related_weaknesses_text = ", ".join(
            f"CWE-{node.get('CWE_ID')} ({node.get('Nature')})" 
            for node in related_weaknesses_nodes
        ) or "N/A"

        text_parts = {
            "Description": get_formatted_complex_text(weakness, 'Description'),
            "Extended Description": get_formatted_complex_text(weakness, 'Extended_Description'),
            "Related Weaknesses": related_weaknesses_text,
            "Common Consequences": format_structured_list(weakness, 'Common_Consequences', 'Consequence', {'Scope': 'Scope', 'Impact': 'Impact'}),
            "Potential Mitigations": get_formatted_complex_text(weakness, 'Potential_Mitigations'),
            "Detection Methods": format_structured_list(weakness, 'Detection_Methods', 'Detection_Method', {'Method': 'Method', 'Effectiveness': 'Effectiveness'}),
            "Demonstrative Examples": format_demonstrative_examples(weakness)
        }
        
        full_text_for_embedding = f"# {metadata['cwe_id']}: {cwe_name}\n"
        full_text_for_embedding += f"**Abstraction**: {metadata['abstraction']} | **Status**: {metadata['status']}\n\n"
        
        for title, content in text_parts.items():
            if content and content != "N/A":
                full_text_for_embedding += f"### {title}\n{content}\n\n"
        
        doc = Document(text=full_text_for_embedding.strip(), metadata=metadata)
        llama_documents.append(doc)

    logging.info(f"Parsing complete. {len(llama_documents)} CWE weakness(es) processed.")
    return llama_documents

# --- Main Execution Block ---
if __name__ == "__main__":
    CWE_FILE_PATH = "C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\cwec_latest.xml"
    OUTPUT_FILE_PATH = 'parsed_cwe_output.txt'
    
    parsed_documents = parse_cwe_from_xml(CWE_FILE_PATH)
    
    if parsed_documents:
        logging.info(f"✅ Parsing successful. Writing {len(parsed_documents)} document(s) to '{OUTPUT_FILE_PATH}'...")
        
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            for i, doc in enumerate(parsed_documents):
                cwe_id_num = doc.metadata.get('cwe_id', 'N/A').split('-')[-1]
                f.write(f"========================= DOCUMENT {i+1} (CWE-{cwe_id_num}) =========================")
                f.write("\n\n--- EXTRACTED METADATA ---\n\n")
                
                # Write metadata
                f.write(str(doc.metadata))
                
                f.write("\n\n\n--- FULL TEXT TO BE EMBEDDED (MARKDOWN FORMAT) ---\n\n")
                f.write(doc.text)
                
                f.write(f"\n\n======================= END OF DOCUMENT {i+1} ========================\n\n\n")
        
        print(f"\n✅ Parsing complete. {len(parsed_documents)} document(s) written to '{OUTPUT_FILE_PATH}'.")
    else:
        print("\n❌ No documents were generated. Please check the logs and the input file.")
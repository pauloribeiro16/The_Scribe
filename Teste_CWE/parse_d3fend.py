# teste_d3fend_full.py

import os
import logging
from typing import List, Dict
from collections import defaultdict
from llama_index.core import Document

try:
    from rdflib import Graph, Namespace, URIRef
    from rdflib.namespace import RDF, RDFS, OWL
except ImportError:
    raise ImportError("rdflib is required for D3FEND parsing. Please run 'pip install rdflib'")

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define namespaces for cleaner queries and output
D3F = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")
NAMESPACES = {
    'd3f': D3F,
    'rdfs': RDFS,
    'owl': OWL,
    'rdf': RDF
}

def get_name(g: Graph, term: URIRef) -> str:
    """Helper to get a human-readable name for a URI."""
    if isinstance(term, URIRef):
        label = g.value(subject=term, predicate=RDFS.label)
        if label:
            return str(label)
        # Fallback to splitting the URI
        return str(term).split('#')[-1]
    return str(term)

def parse_d3fend_full_ontology(file_path: str) -> List[Document]:
    """
    Parses the entire D3FEND ontology, creating enriched Documents for every
    Class, Object Property, and Data Property to make the full knowledge graph searchable.
    """
    logging.info(f"Starting full ontology parsing of D3FEND file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"D3FEND file not found at: {file_path}")
        return []

    g = Graph()
    try:
        g.parse(file_path, format="turtle")
    except Exception as e:
        logging.error(f"Failed to parse the D3FEND TTL file. Error: {e}")
        return []

    all_documents = []

    # --- PRONG 1: PARSE CLASSES (The "Nouns") ---
    class_query = """
        SELECT ?class ?label ?definition ?parent_class
        WHERE {
            ?class a owl:Class .
            FILTER(ISIRI(?class))
            OPTIONAL { ?class rdfs:label ?label . }
            OPTIONAL { ?class d3f:definition ?definition . }
            OPTIONAL { ?class rdfs:subClassOf ?parent_class . FILTER(ISIRI(?parent_class)) }
        }
    """
    class_results = g.query(class_query, initNs=NAMESPACES)
    logging.info(f"Found {len(class_results)} potential classes to process.")

    # Pre-calculate all relationships for each class
    class_relationships = defaultdict(lambda: {'domain_of': [], 'range_of': []})
    
    # ***** START OF FIX *****
    # Corrected the property names from RDFS.domain/range to RDFS.domain/range
    prop_query = """
        SELECT ?prop ?domain ?range
        WHERE {
            ?prop a owl:ObjectProperty .
            OPTIONAL { ?prop rdfs:domain ?domain . }
            OPTIONAL { ?prop rdfs:range ?range . }
            FILTER(ISIRI(?prop) && ISIRI(?domain) && ISIRI(?range))
        }
    """
    for row in g.query(prop_query, initNs=NAMESPACES):
        class_relationships[row.domain]['domain_of'].append(row.prop)
        class_relationships[row.range]['range_of'].append(row.prop)
    # ***** END OF FIX *****

    for row in class_results:
        class_uri = row['class']
        if "http://www.w3.org" in str(class_uri): continue

        class_id = str(class_uri).split('#')[-1]
        label = str(row.label) if row.label else class_id
        definition = str(row.definition) if row.definition else "No definition provided."
        parent_class_name = get_name(g, row.parent_class) if row.parent_class else "Thing"

        relations_text = []
        for prop in sorted(class_relationships[class_uri]['domain_of']):
            prop_range = g.value(subject=prop, predicate=RDFS.range)
            relations_text.append(f"*  `{label}` **{get_name(g, prop)}** `{get_name(g, prop_range)}`")
        for prop in sorted(class_relationships[class_uri]['range_of']):
            prop_domain = g.value(subject=prop, predicate=RDFS.domain)
            relations_text.append(f"*  `{get_name(g, prop_domain)}` **{get_name(g, prop)}** `{label}`")

        enriched_text = (
            f"From D3FEND Ontology:\n"
            f"### Concept: {label} (ID: {class_id})\n\n"
            f"**Is a type of:** {parent_class_name}\n\n"
            f"**Definition:**\n{definition}"
        )
        if relations_text:
            enriched_text += "\n\n**Relationships:**\n" + "\n".join(sorted(list(set(relations_text))))

        metadata = {"source_document": "D3FEND", "entity_type": "Concept/Class", "id": class_id, "label": label}
        all_documents.append(Document(text=enriched_text.strip(), metadata=metadata))

    # --- PRONG 2: PARSE OBJECT PROPERTIES (The "Verbs") ---
    obj_prop_query = """
        SELECT ?prop ?label ?definition ?parent_prop ?inverse_prop ?domain ?range
        WHERE {
            ?prop a owl:ObjectProperty .
            FILTER(ISIRI(?prop))
            OPTIONAL { ?prop rdfs:label ?label . }
            OPTIONAL { ?prop d3f:definition ?definition . }
            OPTIONAL { ?prop rdfs:subPropertyOf ?parent_prop . FILTER(ISIRI(?parent_prop)) }
            OPTIONAL { ?prop owl:inverseOf ?inverse_prop . }
            OPTIONAL { ?prop rdfs:domain ?domain . }
            OPTIONAL { ?prop rdfs:range ?range . }
        }
    """
    prop_results = g.query(obj_prop_query, initNs=NAMESPACES)
    logging.info(f"Found {len(prop_results)} potential object properties to process.")
    
    for row in prop_results:
        prop_uri = row.prop
        if "http://www.w3.org" in str(prop_uri): continue

        prop_id = str(prop_uri).split('#')[-1]
        label = str(row.label) if row.label else prop_id
        definition = str(row.definition) if row.definition else "No definition provided."
        parent_prop_name = get_name(g, row.parent_prop) if row.parent_prop else "None"
        inverse_prop_name = get_name(g, row.inverse_prop) if row.inverse_prop else "None"
        domain_name = get_name(g, row.domain) if row.domain else "Any"
        range_name = get_name(g, row.range) if row.range else "Any"

        enriched_text = (
            f"From D3FEND Ontology:\n"
            f"### Relationship: {label} (ID: {prop_id})\n\n"
            f"**Is a type of relationship:** {parent_prop_name}\n"
            f"**Inverse Relationship:** {inverse_prop_name}\n\n"
            f"**Definition:**\n{definition}\n\n"
            f"**Usage Example:**\n"
            f"*   **Subject (Connects From):** `{domain_name}`\n"
            f"*   **Object (Connects To):** `{range_name}`\n"
            f"*   **Sentence Form:** A `{domain_name}` **{label}** a `{range_name}`."
        )

        metadata = {"source_document": "D3FEND", "entity_type": "Relationship/ObjectProperty", "id": prop_id, "label": label}
        all_documents.append(Document(text=enriched_text.strip(), metadata=metadata))
        
    logging.info(f"Full ontology parsing complete. Total documents created: {len(all_documents)}")
    return all_documents

# --- Main Test Execution Block ---
if __name__ == "__main__":
    D3FEND_FILE_PATH = 'C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\d3fend.txt' 
    if not os.path.exists(D3FEND_FILE_PATH):
        D3FEND_FILE_PATH = 'C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\d3fend.ttl'

    if not os.path.exists(D3FEND_FILE_PATH):
         print(f"❌ Could not find '{D3FEND_FILE_PATH}' or 'd3fend.txt'. Please place the file in the same directory.")
    else:
        parsed_docs = parse_d3fend_full_ontology(D3FEND_FILE_PATH)
        
        if parsed_docs:
            print(f"\n✅ Full ontology parsing successful. Found {len(parsed_docs)} total entities.")
            print("Inspecting a few examples of different types:\n")
            
            process_doc = next((doc for doc in parsed_docs if doc.metadata.get('id') == 'Process'), None)
            if process_doc:
                print(f"========================= EXAMPLE 1: A CLASS ({process_doc.metadata.get('id')}) =========================")
                print(process_doc.text)
                print(f"================================================================================\n")

            executes_doc = next((doc for doc in parsed_docs if doc.metadata.get('id') == 'executes'), None)
            if executes_doc:
                print(f"========================= EXAMPLE 2: A RELATIONSHIP ({executes_doc.metadata.get('id')}) =========================")
                print(executes_doc.text)
                print(f"================================================================================\n")
                
        else:
            print("\n❌ No documents were generated. Please check the logs and the input file content.")
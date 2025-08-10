import os
import logging
import re
from typing import List
from llama_index.core import Document

def parse_dora_from_text(file_path: str) -> List[Document]:
    """
    Parses the DORA text file into granular, enriched, and self-contained Documents
    for each Recital and Article paragraph.
    """
    logging.info(f"Parsing DORA text file with enrichment: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"DORA text file not found at: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Simple cleaning for headers/footers and footnotes
            full_text = re.sub(r'L \d+/\d+\s+EN\s+Official Journal of the European Union\s+\d+\.\d+\.\d+\n', '', f.read())
            full_text = re.sub(r'\(\d+\)', '', full_text) # Remove footnote markers like (1), (23), etc.
    except IOError as e:
        logging.error(f"Failed to read file {file_path}: {e}")
        return []

    llama_documents = []
    
    try:
        recitals_text, main_body = re.split(r'\s*HAVE ADOPTED THIS REGULATION:\s*', full_text, 1)
    except ValueError:
        logging.error("Could not split DORA text at 'HAVE ADOPTED THIS REGULATION:'.")
        return []
        
    # Process Recitals
    recital_matches = re.finditer(r'\((\d+)\)\s*(.*?)(?=\(\d+\)|HAVE ADOPTED)', recitals_text, re.DOTALL)
    for match in recital_matches:
        recital_num = int(match.group(1))
        recital_text = ' '.join(match.group(2).strip().split())
        
        # Text Enrichment
        enriched_text = f"From DORA (Digital Operational Resilience Act):\n### Recital {recital_num}\n\n{recital_text}"
        metadata = { "source_document": "DORA", "type": "Recital", "recital_number": recital_num }
        llama_documents.append(Document(text=enriched_text, metadata=metadata))
            
    # Process Articles
    article_blocks = re.split(r'\n\s*(?=Article \d+)', main_body)
    current_chapter = "Unknown"
    
    for block in article_blocks:
        if not block.strip().startswith("Article"):
            chapter_match = re.search(r'CHAPTER\s+([IVXLCDM]+)\n\s*(.*?)\n', block)
            if chapter_match: current_chapter = f"Chapter {chapter_match.group(1)} - {chapter_match.group(2).strip()}"
            continue

        header_match = re.search(r'Article (\d+)\n\s*(.*?)\n', block)
        if not header_match: continue
            
        article_num = int(header_match.group(1))
        article_title = header_match.group(2).strip()
        content = block[header_match.end():].strip()
        
        para_matches = list(re.finditer(r'^\s*(\d+)\.\s+', content, re.MULTILINE))
        if para_matches:
            for i, match in enumerate(para_matches):
                para_id = match.group(1)
                start = match.end()
                end = para_matches[i+1].start() if i + 1 < len(para_matches) else len(content)
                para_text = ' '.join(content[start:end].strip().split())
                
                # Text Enrichment
                enriched_text = f"From DORA:\n### Article {article_num} ('{article_title}'), Paragraph {para_id}\n\n{para_text}"
                metadata = {
                    "source_document": "DORA", "type": "Article", "chapter": current_chapter,
                    "article_number": str(article_num), "article_title": article_title, "paragraph": para_id
                }
                llama_documents.append(Document(text=enriched_text, metadata=metadata))
        elif content:
            # Text Enrichment for articles without numbered paragraphs
            enriched_text = f"From DORA:\n### Article {article_num} ('{article_title}')\n\n{' '.join(content.split())}"
            metadata = {
                "source_document": "DORA", "type": "Article", "chapter": current_chapter,
                "article_number": str(article_num), "article_title": article_title, "paragraph": "full"
            }
            llama_documents.append(Document(text=enriched_text, metadata=metadata))

    logging.info(f"Parsing of DORA complete. {len(llama_documents)} documents created.")
    return llama_documents
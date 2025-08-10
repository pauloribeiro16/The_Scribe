# teste_iso.py

import os
import re
import logging
from typing import List
from llama_index.core import Document

# Configuração do logging para melhor depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#
# ESTA É A SUA FUNÇÃO ORIGINAL, USANDO A LÓGICA DE PARSING QUE FUNCIONA.
# A ÚNICA MODIFICAÇÃO É GARANTIR QUE OS CHECKS SÃO SEGUROS E A SAÍDA É ENRIQUECIDA.
#
def parse_iso_27002(file_path: str) -> List[Document]:
    """
    Analisa o texto completo da ISO/IEC 27002:2022 usando a lógica de parsing validada.
    """
    logging.info(f"A iniciar a análise do ficheiro ISO/IEC 27002:2022: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"Ficheiro de texto ISO 27002 não encontrado em: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except IOError as e:
        logging.error(f"Falha ao ler o ficheiro de texto {file_path}: {e}")
        return []

    llama_documents = []
    source_filename = os.path.basename(file_path)

    # Isolar a secção principal de controlos (Sua lógica original e correta)
    try:
        main_content_match = re.search(r'5\s+Organizational controls\s*\n\s*5\.1([\s\S]+?)Annex A', full_text, re.DOTALL)
        if not main_content_match:
            logging.error("Não foi possível isolar o conteúdo das Cláusulas 5-8. Verifique os marcadores '5 Organizational controls' e 'Annex A'.")
            return []
        # Adicionar o início do primeiro controlo de volta para que seja incluído na pesquisa
        main_content = "5.1" + main_content_match.group(1)
    except Exception as e:
        logging.error(f"Erro inesperado ao extrair o conteúdo principal: {e}")
        return []

    themes = {
        '5': 'Organizational controls',
        '6': 'People controls',
        '7': 'Physical controls',
        '8': 'Technological controls',
    }

    # Padrão para encontrar cada bloco de controlo individualmente.
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

        # Parsing seguro para cada secção, para evitar erros
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

        # Aplicar o princípio do "Chunk Enriquecido"
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
        
    logging.info(f"Análise concluída. Foram criados com sucesso {len(llama_documents)} blocos de documentos.")
    return llama_documents


# --- Bloco de Execução para Teste Autocontido ---
if __name__ == "__main__":
    ISO_FILE_PATH = 'C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\ISO_27002.txt'
    OUTPUT_FILE_PATH = 'C:\\Users\\paulo.ribeiro\\OneDrive - Instituto CCG ZGDV\\Ambiente de Trabalho\\Projetos\\SuperRAG\\Teste_CWE\\parsed_iso_27002_output.txt'

    parsed_docs = parse_iso_27002(ISO_FILE_PATH)
    
    if parsed_docs:
        logging.info(f"✅ Análise bem-sucedida. A gravar {len(parsed_docs)} documento(s) em '{OUTPUT_FILE_PATH}'...")

        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            for i, doc in enumerate(parsed_docs):
                control_id_num = doc.metadata.get('control_id', 'N/A')
                f.write(f"========================= DOCUMENT {i+1} (Control {control_id_num}) =========================")
                f.write("\n\n--- EXTRACTED METADATA ---\n\n")
                f.write(str(doc.metadata))
                f.write("\n\n\n--- FULL TEXT TO BE EMBEDDED (MARKDOWN FORMAT) ---\n\n")
                f.write(doc.text)
                f.write(f"\n\n======================= END OF DOCUMENT {i+1} ========================\n\n\n")

        print(f"\n✅ Análise concluída. {len(parsed_docs)} documento(s) gravado(s) em '{OUTPUT_FILE_PATH}'.")
    else:
        print("\n❌ Nenhum documento foi gerado. Verifique os logs e o ficheiro de entrada.")
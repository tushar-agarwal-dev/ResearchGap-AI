import re
import logging
from typing import List, Dict, Any
from .insights_extractor import partition_sections

logger = logging.getLogger(__name__)

def semantic_chunking(text: str, max_chunk_size: int = 4000) -> List[Dict[str, Any]]:
    """
    Intelligently chunks a paper by section and then by paragraph boundaries.
    Preserves context and avoids naive fixed-size chunking.
    """
    logger.info("Pipeline Trace: Partitioning text into sections...")
    sections = partition_sections(text)
    logger.info(f"Pipeline Trace: Detected {len(sections)} sections.")
    chunks = []
    
    for section_name, section_text in sections.items():
        if not section_text.strip():
            continue
            
        paragraphs = re.split(r'\n\s*\n', section_text)
        logger.info(f"Pipeline Trace: Section '{section_name}' has {len(paragraphs)} paragraphs.")
        current_chunk_text = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If adding this paragraph exceeds limit, save current chunk and start new one
            if len(current_chunk_text) + len(para) > max_chunk_size and current_chunk_text:
                chunks.append({
                    "section": section_name,
                    "text": current_chunk_text.strip(),
                    "position": len(chunks) + 1
                })
                current_chunk_text = para + "\n\n"
            else:
                current_chunk_text += para + "\n\n"
                
        # Add remaining text
        if current_chunk_text.strip():
            chunks.append({
                "section": section_name,
                "text": current_chunk_text.strip(),
                "position": len(chunks) + 1
            })
            
    return chunks

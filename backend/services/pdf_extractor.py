import io
import logging
from typing import Dict, Any

import fitz  # PyMuPDF
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

def _extract_with_pdfplumber(pdf_bytes: bytes) -> Dict[str, Any]:
    try:
        combined_text = ""
        page_wise_text = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    combined_text += text + "\n\n"
                    page_wise_text.append({"page": page_number, "text": text})
        
        return {
            "page_wise_text": page_wise_text,
            "complete_text": combined_text,
            "extraction_confidence": 0.85 if combined_text else 0.0
        }
    except Exception as e:
        logger.error(f"pdfplumber fallback failed: {e}")
        return {"error": "extraction_failed", "extraction_confidence": 0.0}

def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """Extract text from PDF using PyMuPDF, falling back to pdfplumber."""
    logger.info("Pipeline Trace: Initializing PDF extraction via PyMuPDF...")
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_wise_text = []
        combined_text = ""
        logger.info(f"Pipeline Trace: PDF opened. Page count: {len(doc)}")

        for page_number, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))
            
            page_text = ""
            for b in blocks:
                if b[4].strip():
                    page_text += b[4] + "\n\n"
            
            page_wise_text.append({"page": page_number, "text": page_text})
            combined_text += page_text

        doc.close()
        
        if not combined_text.strip():
            logger.warning("Pipeline Trace: PyMuPDF returned empty text, falling back to pdfplumber")
            return _extract_with_pdfplumber(pdf_bytes)
            
        logger.info(f"Pipeline Trace: PDF extraction successful. Total chars: {len(combined_text)}")
        return {
            "page_wise_text": page_wise_text,
            "complete_text": combined_text,
            "extraction_confidence": 0.95
        }
    except Exception as e:
        logger.error(f"Pipeline Trace: PyMuPDF extraction failed: {e}, falling back to pdfplumber")
        return _extract_with_pdfplumber(pdf_bytes)


def extract_text_from_docx(docx_bytes: bytes) -> Dict[str, Any]:
    try:
        doc = Document(io.BytesIO(docx_bytes))
        full_text = [para.text for para in doc.paragraphs]
        combined_text = "\n\n".join(full_text)
        return {
            "page_wise_text": [{"page": 1, "text": combined_text}],
            "complete_text": combined_text,
            "extraction_confidence": 0.90 if combined_text else 0.0
        }
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return {"error": "extraction_failed", "extraction_confidence": 0.0}


def extract_content(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_bytes)
    else:
        return {"error": "unsupported_format", "extraction_confidence": 0.0}

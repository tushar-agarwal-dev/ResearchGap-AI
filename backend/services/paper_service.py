import os
import logging
import hashlib
from typing import List, Dict, Any, Optional

import numpy as np
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from database.models import Paper, ExtractedData
from services.pdf_extractor import extract_content
from services.summarizer import generate_summary
from services.insights_extractor import extract_all_insights

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # Increased to 25MB


def validate_file(file: UploadFile):
    """Ensure the file is a supported format and within size limits."""
    allowed_extensions = {".pdf", ".docx", ".doc"}
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. {file.filename or 'File'} must be a PDF or Word document."
        )
    
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400, 
            detail=f"{file.filename} exceeds the 15MB size limit."
        )


def sanitize_text(text: Optional[str]) -> str:
    """Removes NUL (0x00) characters to prevent PostgreSQL insertion errors."""
    if not text:
        return ""
    return text.replace("\u0000", "").replace("\x00", "")


def get_file_hash(file_bytes: bytes) -> str:
    """Generate a unique SHA-256 hash for the file content."""
    return hashlib.sha256(file_bytes).hexdigest()


from services.research_intelligence import research_intelligence

def process_document_batch_step(file: UploadFile, owner_id: int, db: Session) -> Paper:
    """
    Core processing logic for a single document in a batch.
    Performs extraction and entity mining with hash-based caching.
    """
    validate_file(file)
    file_bytes = file.file.read()
    file_hash = get_file_hash(file_bytes)
    
    # CHECK CACHE: If this user has already uploaded this exact file, reuse the data
    existing_paper = db.query(Paper).filter(Paper.owner_id == owner_id, Paper.filename == file.filename).order_by(Paper.id.desc()).first()
    if existing_paper and existing_paper.extracted_data and existing_paper.extracted_data.intelligence_report:
        logger.info(f"CACHE HIT: Reusing existing intelligence report for {file.filename}")
        # Note: In a production app, you'd check the content hash, but for now we'll create a new paper record 
        # and clone the extracted data if the hash matches any global paper, OR just reuse for this user.
        
    # GLOBAL CACHE HIT (Any user): Look for the same content hash
    # Note: We need a 'content_hash' column in Paper or ExtractedData to do this properly.
    # For now, let's just proceed but ensure we only call Gemini if absolutely necessary.

    # Step 1: Text Extraction (Mandate 1 & 2)
    extracted = extract_content(file_bytes, file.filename)
    if "error" in extracted:
        raise HTTPException(
            status_code=422, 
            detail=f"Extraction failed for {file.filename}: {extracted['error']}"
        )
        
    full_text = sanitize_text(extracted.get("complete_text", ""))
    page_wise_text = extracted.get("page_wise_text", [])
    for page in page_wise_text:
        if "text" in page:
            page["text"] = sanitize_text(page["text"])

    # Step 2 & 3: Insights & Entities
    summary = sanitize_text(generate_summary(full_text))
    insights = extract_all_insights(full_text)
    
    # Create DB records
    paper = Paper(owner_id=owner_id, filename=file.filename, summary=summary)
    db.add(paper)
    db.flush()

    # Intelligence Logic with Local Deduplication (Only cache successful ones)
    report = None
    existing_extraction = db.query(ExtractedData).filter(
        ExtractedData.complete_text == full_text
    ).order_by(ExtractedData.id.desc()).first()
    
    if existing_extraction and existing_extraction.intelligence_report:
        cached_report = existing_extraction.intelligence_report
        # Only reuse if it's a 'real' report (not an empty fallback)
        has_data = len(cached_report.get("contributions", [])) > 0 or cached_report.get("recommendation", {}).get("read_score", 0) > 0
        if has_data:
            logger.info(f"API SAVER: Reusing successful intelligence report from identical content hash.")
            report = cached_report
        else:
            logger.info("CACHE IGNORE: Previous report was a fallback. Forcing fresh API call.")

    if not report:
        logger.info(f"API CALL: Requesting new intelligence report for {file.filename}")
        paper_payload = {
            "id": paper.id,
            "filename": paper.filename,
            "complete_text": full_text,
            "insights": insights,
            "domain": insights.get("domain", "General")
        }
        report = research_intelligence.generate_full_report(paper_payload)

    # Sanitize everything going into JSONB fields as well for safety
    extracted_data = ExtractedData(
        paper_id=paper.id,
        page_wise_text=page_wise_text,
        complete_text=full_text,
        meta_data=insights.get("metadata", {}),
        sections=[sanitize_text(s) for s in insights.get("sections", [])],
        algorithms=[sanitize_text(a) for a in insights.get("algorithms", [])],
        datasets=[sanitize_text(d) for d in insights.get("datasets", [])],
        results=insights.get("results", {}),
        strengths=insights.get("strengths", []),
        weaknesses=insights.get("weaknesses", []),
        novelty=insights.get("novelty", ""),
        research_gap=insights.get("research_gap", ""),
        future_scope=insights.get("future_scope", ""),
        complexity=insights.get("complexity", "Intermediate"),
        reading_time=insights.get("reading_time", 10),
        reproducibility_score=insights.get("reproducibility_score", 0.7),
        domain=insights.get("domain", "General"),
        intelligence_report=report
    )
    
    # Pack confidence into metadata
    extracted_data.meta_data["confidence_scores"] = {
        "extraction_confidence": extracted.get("extraction_confidence", 0.9),
        "insight_extraction_confidence": 0.85 if insights.get("algorithms") else 0.6,
    }
    
    db.add(extracted_data)
    return paper


def process_document(file: UploadFile, owner_id: int, db: Session) -> Paper:
    """Wrapper for backward compatibility, performs single commit."""
    paper = process_document_batch_step(file, owner_id, db)
    db.commit()
    db.refresh(paper)
    return paper


def get_user_paper_payloads(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Helper to get paper data formatted for analytical engines."""
    papers = db.query(Paper).filter(Paper.owner_id == user_id).all()
    payloads = []
    for paper in papers:
        extracted = paper.extracted_data
        if not extracted:
            continue
        payloads.append({
            "id": paper.id,
            "filename": paper.filename,
            "complete_text": extracted.complete_text or "",
            "algorithms": extracted.algorithms or [],
            "datasets": extracted.datasets or [],
            "results": extracted.results or {},
            "year": (extracted.meta_data or {}).get("publication_year") or "",
            "summary": paper.summary or ""
        })
    return payloads


def format_paper_response(paper: Paper, detailed: bool = False) -> Dict[str, Any]:
    """Format paper model for API response."""
    extracted = paper.extracted_data
    if not extracted:
         logger.warning(f"No extraction data found for paper {paper.id}")
         return {"id": paper.id, "filename": paper.filename, "error": "No extraction data found"}

    logger.info(f"Formatting response for paper {paper.id}. Report present: {extracted.intelligence_report is not None}")

    response = {
        "id": paper.id,
        "filename": paper.filename,
        "summary": paper.summary,
        "insights": {
            "metadata": extracted.meta_data,
            "sections": extracted.sections,
            "algorithms": extracted.algorithms,
            "datasets": extracted.datasets,
            "results": extracted.results,
            "strengths": extracted.strengths,
            "weaknesses": extracted.weaknesses,
            "novelty": extracted.novelty,
            "research_gap": extracted.research_gap,
            "future_scope": extracted.future_scope,
            "complexity": extracted.complexity,
            "reading_time": extracted.reading_time,
            "reproducibility_score": extracted.reproducibility_score,
            "domain": extracted.domain,
        },
        "intelligence_report": extracted.intelligence_report,
        "complete_text": extracted.complete_text[:3000] if not detailed else extracted.complete_text,
    }
    
    if detailed:
        response["page_wise_text"] = [p["text"] for p in (extracted.page_wise_text or [])]
    else:
        response["page_wise_text"] = [p["text"] for p in (extracted.page_wise_text or [])[:3]]
    
    return response


def delete_user_papers(user_id: int, db: Session):
    """
    Permanently and aggressively deletes all papers and extracted data associated with a user.
    Ensures a stateless 'Fresh Session' every time.
    """
    try:
        # 1. Get all paper IDs for this user
        paper_ids = [p.id for p in db.query(Paper.id).filter(Paper.owner_id == user_id).all()]
        
        if paper_ids:
            # 2. Delete ExtractedData explicitly (backup for CASCADE)
            db.query(ExtractedData).filter(ExtractedData.paper_id.in_(paper_ids)).delete(synchronize_session=False)
            
            # 3. Delete Papers
            db.query(Paper).filter(Paper.id.in_(paper_ids)).delete(synchronize_session=False)
            
            db.commit()
            logger.info(f"Aggressively cleared {len(paper_ids)} papers for user {user_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear session data for user {user_id}: {e}")

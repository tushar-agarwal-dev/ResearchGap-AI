from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Paper
from routes.deps import get_current_user
from services import paper_service
from models.paper import (
    PaperResponse,
    CompareRequest,
    CompareResponse,
    CompareRow,
)

router = APIRouter(tags=["papers"])


@router.post("/ingest")
async def ingest_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unified ingestion endpoint for one or many research documents.
    Atomic operation: All files are processed before a single commit.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    filenames = [file.filename for file in files]
    
    try:
        # Pre-process: Remove existing papers with same names for THIS user
        # This avoids session conflicts during the fresh ingestion loop
        db.query(Paper).filter(
            Paper.owner_id == current_user.id, 
            Paper.filename.in_(filenames)
        ).delete(synchronize_session=False)
        db.flush()

        processed_papers = []
        for file in files:
            # Prepare paper objects
            paper = paper_service.process_document_batch_step(file, current_user.id, db)
            processed_papers.append(paper)
        
        db.commit()
        # Refresh to populate auto-generated fields
        for p in processed_papers:
            db.refresh(p)
            
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception(f"Ingestion critical failure: {e}")
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")

    return {
        "success": True,
        "message": f"Successfully processed {len(processed_papers)} document(s).",
        "data": [paper_service.format_paper_response(p) for p in processed_papers],
    }


@router.get("/papers")
def list_papers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_papers = db.query(Paper).filter(Paper.owner_id == current_user.id).all()
    return {
        "success": True,
        "data": [paper_service.format_paper_response(p) for p in user_papers]
    }


@router.get("/papers/{paper_id}")
def get_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id, Paper.owner_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    return {
        "success": True,
        "data": paper_service.format_paper_response(paper, detailed=True)
    }


@router.delete("/papers/{paper_id}")
def delete_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id, Paper.owner_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    db.delete(paper)
    db.commit()
    return {
        "success": True,
        "message": "Paper deleted successfully."
    }


from services.research_intelligence import research_intelligence

@router.post("/papers/{paper_id}/analyze")
def analyze_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id, Paper.owner_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    extracted = paper.extracted_data
    if not extracted:
         raise HTTPException(status_code=422, detail="No extracted text found for analysis.")

    paper_payload = {
        "id": paper.id,
        "filename": paper.filename,
        "complete_text": extracted.complete_text,
        "insights": {
            "reproducibility_score": extracted.reproducibility_score,
            "domain": extracted.domain
        },
        "domain": extracted.domain
    }
    
    report = research_intelligence.generate_full_report(paper_payload)
    extracted.intelligence_report = report
    db.commit()
    
    return {
        "success": True,
        "data": paper_service.format_paper_response(paper)
    }


@router.post("/compare", response_model=CompareResponse)
def compare_papers(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if len(payload.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two paper IDs.")

    requested_ids = sorted(set(payload.paper_ids))
    papers = (
        db.query(Paper)
        .filter(Paper.owner_id == current_user.id, Paper.id.in_(requested_ids))
        .all()
    )
    
    found_ids = {paper.id for paper in papers}
    missing_ids = [pid for pid in requested_ids if pid not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Papers not found for IDs: {', '.join(str(i) for i in missing_ids)}",
        )

    comparison_rows = []
    for paper in papers:
        extracted = paper.extracted_data
        comparison_rows.append(
            CompareRow(
                paper_id=paper.id,
                filename=paper.filename,
                methodology=extracted.algorithms or [],
                dataset=extracted.datasets or [],
                accuracy=(extracted.results or {}).get("metrics", {}).get("accuracy", "N/A"),
            )
        )

    return CompareResponse(comparison=comparison_rows)

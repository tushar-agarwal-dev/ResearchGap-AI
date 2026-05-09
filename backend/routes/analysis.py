from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User
from routes.deps import get_current_user
from services import paper_service
from services import intelligent_analysis as ia_service
from services.semantic_search import SemanticSearchService
from services.clustering import cluster_papers
from services.citation import build_citation_network

# Phase 3 Engines
from services.gap_engine import deep_gap_analysis
from services.novelty_engine import compute_novelty_and_trends
from services.proposal_engine import generate_research_proposal
from services.insight_engine import generate_research_insights
from services.research_chat import research_assistant

from models.analysis import (
    DashboardResponse,
    SemanticSearchRequest,
    SearchResponse,
    SearchMatch,
    TopicCluster,
    CitationNetworkResponse,
    DeepGapResponse,
    NoveltyResponse,
    InsightResponse,
    ResearchChatRequest,
    ResearchChatResponse,
    ProposalRequest,
    ProposalResponse,
    GapItem
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Service instances
semantic_search_service = SemanticSearchService()


@router.get("/comprehensive")
def analysis_comprehensive(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Comprehensive analysis following Mandate 9's strict structure."""
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    if not payloads:
        return {
            "summary": "No papers available for analysis.",
            "entities": {"algorithms": [], "datasets": [], "metrics": []},
            "gaps": [],
            "trends": [],
            "confidence_scores": {
                "extraction_confidence": 0.0,
                "similarity_confidence": 0.0,
                "gap_detection_confidence": 0.0
            }
        }

    # Extract all entities across corpus
    all_algos = sorted(list(set([a for p in payloads for a in p.get("algorithms", [])])))
    all_datasets = sorted(list(set([d for p in payloads for d in p.get("datasets", [])])))
    
    # Gaps with evidence (Mandate 3)
    gaps = deep_gap_analysis(payloads)
    
    # Trends (Mandate 6)
    trends = ia_service.detect_research_shifts(payloads)
    
    # Confidence (Mandate 4)
    avg_gap_conf = sum([g["confidence"] for g in gaps]) / len(gaps) if gaps else 0.8
    
    # Summary (Mandate 7)
    paper_list = ", ".join([p["filename"] for p in payloads[:3]])
    summary = f"Analysis of {len(payloads)} documents (including {paper_list}). "
    if all_algos:
        summary += f"Dominant methodologies include {', '.join(all_algos[:3])}. "
    
    return {
        "summary": summary,
        "entities": {
            "algorithms": all_algos,
            "datasets": all_datasets,
            "metrics": ["Accuracy", "F1-Score", "Precision", "Recall"] # Placeholder for extracted metrics
        },
        "gaps": gaps,
        "trends": trends,
        "confidence_scores": {
            "extraction_confidence": 0.9, # Heuristic
            "similarity_confidence": 0.85, # Heuristic
            "gap_detection_confidence": round(avg_gap_conf, 2)
        }
    }


@router.get("/deep-gaps", response_model=DeepGapResponse)
def analysis_deep_gaps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    gaps = deep_gap_analysis(payloads)
    avg_conf = sum([g["confidence"] for g in gaps]) / len(gaps) if gaps else 0.0
    return {
        "success": True,
        "data": [GapItem(**g) for g in gaps],
        "confidence_scores": {
            "extraction_confidence": 0.9,
            "similarity_confidence": 0.85,
            "gap_detection_confidence": round(avg_conf, 2)
        }
    }


@router.get("/novelty", response_model=NoveltyResponse)
def analysis_novelty(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    novelty = compute_novelty_and_trends(payloads)
    return {
        "success": True,
        "data": novelty
    }


@router.get("/insights", response_model=InsightResponse)
def analysis_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    insights = generate_research_insights(payloads)
    return {
        "success": True,
        "data": insights
    }


@router.post("/research-chat", response_model=ResearchChatResponse)
def analysis_research_chat(
    payload: ResearchChatRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    answer = research_assistant.ask_question(payload.query, payloads)
    return {
        "success": True,
        "data": answer
    }


@router.post("/proposal", response_model=ProposalResponse)
def analysis_proposal(
    payload: ProposalRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    requested_ids = set(payload.paper_ids)
    all_papers = paper_service.get_user_paper_payloads(current_user.id, db)
    
    if requested_ids:
        selected_papers = [p for p in all_papers if p["id"] in requested_ids]
        if not selected_papers:
            raise HTTPException(status_code=404, detail="Requested papers not found.")
    else:
        selected_papers = all_papers
        
    proposal = generate_research_proposal(selected_papers)
    return {
        "success": True,
        "data": proposal
    }


# --- Dashboard & Helper Endpoints ---

@router.get("/dashboard", response_model=DashboardResponse)
def analysis_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    if not payloads:
        return {
            "keywords": [],
            "yearly_topics": [],
            "method_shifts": [],
            "gaps": [],
            "similar_pairs": [],
            "clusters": [],
            "citation_network": {"nodes": [], "links": []}
        }

    return {
        "keywords": ia_service.keyword_frequency([p["complete_text"] for p in payloads]),
        "yearly_topics": ia_service.trending_topics_by_year(payloads),
        "method_shifts": ia_service.detect_research_shifts(payloads),
        "gaps": ia_service.detect_research_gaps(payloads),
        "similar_pairs": ia_service.paper_similarity_matrix(payloads),
        "clusters": cluster_papers(payloads),
        "citation_network": build_citation_network(payloads),
    }


@router.post("/semantic-search", response_model=SearchResponse)
def semantic_search(
    payload: SemanticSearchRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    if not payloads:
        return {"matches": []}
        
    semantic_search_service.build_index(payloads)
    matches = semantic_search_service.search(payload.query, payload.limit)
    
    paper_map = {p["id"]: p["filename"] for p in payloads}
    enriched_matches = [
        SearchMatch(
            paper_id=m["paper_id"],
            filename=paper_map.get(m["paper_id"], "Unknown"),
            score=round(m["score"], 4)
        )
        for m in matches
    ]
    return {"matches": enriched_matches}


@router.get("/clustering", response_model=List[TopicCluster])
def analysis_clustering(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    return cluster_papers(payloads)


@router.get("/citation-network", response_model=CitationNetworkResponse)
def analysis_citation_network(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payloads = paper_service.get_user_paper_payloads(current_user.id, db)
    return build_citation_network(payloads)

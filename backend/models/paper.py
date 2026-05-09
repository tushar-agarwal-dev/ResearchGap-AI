from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PaperInsight(BaseModel):
    metadata: Dict[str, Any]
    sections: List[str]
    algorithms: List[str]
    datasets: List[str]
    results: Dict[str, Any]
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    novelty: Optional[str] = None
    research_gap: Optional[str] = None
    future_scope: Optional[str] = None
    complexity: Optional[str] = None
    reading_time: Optional[int] = None
    reproducibility_score: Optional[float] = None
    domain: Optional[str] = None


class PaperResponse(BaseModel):
    id: int
    filename: str
    summary: Optional[str] = None
    insights: Optional[PaperInsight] = None
    intelligence_report: Optional[Dict[str, Any]] = None
    complete_text: Optional[str] = None
    page_wise_text: Optional[List[str]] = None


class CompareRequest(BaseModel):
    paper_ids: List[int]


class CompareRow(BaseModel):
    paper_id: int
    filename: str
    methodology: List[str]
    dataset: List[str]
    accuracy: str


class CompareResponse(BaseModel):
    comparison: List[CompareRow]

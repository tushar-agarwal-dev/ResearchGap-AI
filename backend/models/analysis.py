from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class KeywordFrequency(BaseModel):
    keyword: str
    count: int
    frequency: float

class TopicTrend(BaseModel):
    keyword: str
    count: int

class YearlyTrend(BaseModel):
    year: str
    top_topics: List[TopicTrend]

class MethodShift(BaseModel):
    trend: str
    from_year: str
    to_year: str
    delta: int

class PaperSimilarity(BaseModel):
    paper_a_id: int
    paper_a_name: str
    paper_b_id: int
    paper_b_name: str
    similarity: float

class ClusterPaper(BaseModel):
    id: int
    filename: str

class TopicCluster(BaseModel):
    cluster_id: int
    papers: List[ClusterPaper]

class CitationNode(BaseModel):
    id: int
    label: str

class CitationLink(BaseModel):
    source: int
    target: int
    weight: float

class CitationNetworkResponse(BaseModel):
    nodes: List[CitationNode]
    links: List[CitationLink]

class LitReviewRequest(BaseModel):
    paper_ids: List[int]

class LitReviewResponse(BaseModel):
    review: str

class DashboardResponse(BaseModel):
    keywords: List[KeywordFrequency]
    yearly_topics: List[YearlyTrend]
    method_shifts: List[MethodShift]
    gaps: List[str]
    similar_pairs: List[PaperSimilarity]
    clusters: Optional[List[TopicCluster]] = None
    citation_network: Optional[CitationNetworkResponse] = None

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchMatch(BaseModel):
    paper_id: int
    filename: str
    score: float

class SearchResponse(BaseModel):
    matches: List[SearchMatch]

# --- Phase 3 Models ---

class GapItem(BaseModel):
    gap_type: str
    explanation: str
    evidence: str
    confidence: float

class DeepGapResponse(BaseModel):
    success: bool
    data: List[GapItem]
    confidence_scores: Dict[str, float]
    error: Optional[str] = None

class NoveltyItem(BaseModel):
    paper_id: int
    filename: str
    novelty_score: float

class NoveltyResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class InsightResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class ProposalRequest(BaseModel):
    paper_ids: List[int]

class ProposalResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class ResearchChatRequest(BaseModel):
    query: str

class ResearchChatResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class GeneratePaperRequest(BaseModel):
    paper_ids: List[int]

class GeneratePaperResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

from typing import List, Dict, Any
from .novelty_engine import compute_novelty_and_trends

def generate_research_insights(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not papers:
        return {}

    novelty_data = compute_novelty_and_trends(papers)
    
    # Methodology evolution narrative
    methods = [m for p in papers for m in p.get("algorithms", [])]
    unique_methods = sorted(list(set(methods)))

    return {
        "summary_narrative": f"The corpus consists of {len(papers)} papers covering methods such as {', '.join(unique_methods[:5])}.",
        "hot_topics": novelty_data.get("over_explored_topics", []),
        "cold_topics": novelty_data.get("emerging_topics", []),
        "novelty_scores": novelty_data.get("novelty_scores", [])
    }

from typing import List, Dict, Any


def generate_literature_review(papers: List[Dict[str, Any]]):
    if not papers:
        return "No papers provided for literature review."

    # Logic to aggregate insights and structure a review
    review = "# Literature Review Summary\n\n"
    review += f"This review covers {len(papers)} selected research papers.\n\n"
    
    review += "## Key Methodologies\n"
    all_algos = set()
    for p in papers:
        all_algos.update(p.get("algorithms", []))
    review += f"- The researchers predominantly utilized: {', '.join(all_algos) or 'various custom methods'}.\n\n"
    
    review += "## Dataset Landscape\n"
    all_datasets = set()
    for p in papers:
        all_datasets.update(p.get("datasets", []))
    review += f"- Common datasets across these studies include: {', '.join(all_datasets) or 'proprietary or unspecified datasets'}.\n\n"
    
    review += "## Paper Summaries\n"
    for p in papers:
        review += f"### {p['filename']}\n"
        review += f"**Key Insights:** {p.get('summary', 'Summary not available')[:500]}...\n\n"
        
    review += "## Research Trends & Gaps\n"
    from .intelligent_analysis import detect_research_gaps
    gaps = detect_research_gaps(papers)
    review += "Identified gaps in current literature:\n"
    for gap in gaps:
        review += f"- {gap}\n"
        
    return review

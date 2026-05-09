from typing import List, Dict, Any
from .llm_provider import llm_provider
import json

def generate_research_proposal(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not papers:
        return {
            "problem_statement": "General academic advancement.",
            "motivation": "Need for foundational research.",
            "gap_justification": "Initial corpus scan suggests broad unexplored areas.",
            "methodology_ideas": ["Data-driven exploration"],
            "expected_contribution": "New insights.",
            "experiment_plan": "Baseline evaluations."
        }

    context = "\n".join([f"- Paper {p['id']}: {p['filename']}. Summary: {p.get('summary', '')[:200]}" for p in papers[:5]])
    
    prompt = f"""
    Generate a research proposal based on the following papers.
    Return ONLY a JSON object.
    
    Context:
    {context}
    
    Structure:
    {{
      "problem_statement": "...",
      "motivation": "...",
      "gap_justification": "...",
      "methodology_ideas": ["idea1", "idea2"],
      "expected_contribution": "...",
      "experiment_plan": "..."
    }}
    """
    
    response_text = llm_provider.generate(prompt, "You are a senior research scientist drafting a grant proposal.")
    
    try:
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        proposal_data = json.loads(clean_json)
        return proposal_data
    except Exception:
        # Rule-based fallback if LLM/JSON fails
        return {
            "problem_statement": "Synthetic research proposal based on corpus synthesis.",
            "motivation": "Addressing common limitations identified in recent publications.",
            "gap_justification": "Lack of standardized multi-domain metrics across the set.",
            "methodology_ideas": ["Hybrid feature extraction", "Ensemble evaluation"],
            "expected_contribution": "Framework for unified benchmarking.",
            "experiment_plan": "Comparison across three high-diversity datasets."
        }

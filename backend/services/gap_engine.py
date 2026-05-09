from typing import List, Dict, Any
from .llm_provider import llm_provider
from collections import Counter
import json
import re

VALID_GAP_TYPES = [
    "Missing Evaluation Gap",
    "Missing Combination Gap",
    "Underrepresented Domain Gap"
]


def _extract_snippet(text: str, keyword: str, context_chars: int = 200) -> str:
    """Extract a snippet of text around a keyword as evidence."""
    match = re.search(rf".{{0,{context_chars}}}{re.escape(keyword)}.{{0,{context_chars}}}", text, re.IGNORECASE | re.DOTALL)
    if match:
        return f"...{match.group(0).strip()}..."
    return ""


from services.verification_layer import verify_evidence_span, calculate_gap_confidence


def deep_gap_analysis(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Strict research gap analysis with evidence verification (Maturity Fix 1 & 2)."""
    if not papers:
        return []

    gaps = []
    full_corpus_text = " ".join([p.get("complete_text", "").lower() for p in papers])
    all_metrics = []
    for p in papers:
        if isinstance(p.get("results"), dict):
            all_metrics.extend(p["results"].get("metrics", {}).keys())

    # 1. Heuristic Gaps
    # Missing Evaluation Gap
    if "robustness" not in all_metrics:
        gaps.append({
            "gap_type": "Missing Evaluation Gap",
            "explanation": "Corpus lacks robustness metrics.",
            "evidence": "Grounded heuristic: 0 matches for 'robustness' in metrics dictionary.",
            "confidence": calculate_gap_confidence("Missing Evaluation Gap", 1.0, True)
        })

    # 2. AI Reasoning Layer with Verification
    paper_context = "\n".join([f"ID {p['id']}: {p['filename']}. Algos: {p.get('algorithms')}." for p in papers[:5]])
    prompt = f"Identify 2 research gaps in: {paper_context}\nValid: {VALID_GAP_TYPES}\nReturn ONLY JSON array."
    
    ai_raw = llm_provider.generate(prompt, "Analytical engine. Return JSON.")
    
    try:
        ai_data = json.loads(ai_raw.replace("```json", "").replace("```", "").strip())
        for g in ai_data:
            if g.get("gap_type") in VALID_GAP_TYPES:
                # MANDATORY VERIFICATION (Maturity Gap 1)
                verification = verify_evidence_span(full_corpus_text, g.get("evidence", ""))
                
                # RE-CALCULATE CONFIDENCE (Maturity Gap 2)
                g["confidence"] = calculate_gap_confidence(
                    g["gap_type"], 
                    verification["score"], 
                    heuristic_signal=False
                )
                
                if verification["is_verified"]:
                    g["evidence"] = verification["match"] # Replace with exact span
                else:
                    g["explanation"] += " [UNVERIFIED EVIDENCE]"
                
                gaps.append(g)
    except:
        pass

    return gaps

import difflib
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def verify_evidence_span(source_text: str, evidence_snippet: str, threshold: float = 0.85) -> Dict[str, Any]:
    """
    Validates if the provided evidence snippet exists in the source text.
    Returns the best matching span and a verification score.
    """
    if not evidence_snippet or not source_text:
        return {"is_verified": False, "score": 0.0, "match": ""}

    # Clean strings for better matching
    clean_source = " ".join(source_text.split()).lower()
    clean_snippet = " ".join(evidence_snippet.split()).lower()

    if clean_snippet in clean_source:
        return {"is_verified": True, "score": 1.0, "match": evidence_snippet}

    # Fuzzy match if exact match fails (handles slight AI paraphrasing)
    # difflib.get_close_matches isn't ideal for long spans, so we use a sequence matcher approach
    matcher = difflib.SequenceMatcher(None, clean_source, clean_snippet)
    match = matcher.find_longest_match(0, len(clean_source), 0, len(clean_snippet))
    
    score = match.size / len(clean_snippet) if len(clean_snippet) > 0 else 0
    
    return {
        "is_verified": score >= threshold,
        "score": round(score, 4),
        "match": source_text[match.a : match.a + match.size] if score > 0.5 else ""
    }

def calculate_extraction_confidence(extracted_data: Dict[str, Any]) -> float:
    """
    Formula: 1.0 - (Empty Section Penalty + Layout Complexity Penalty)
    """
    text = extracted_data.get("complete_text", "")
    if not text: return 0.0
    
    # Penalize for very short text or lack of structure
    length_score = min(1.0, len(text) / 5000)
    structure_penalty = 0.0
    mandatory_sections = ["introduction", "methodology", "results"]
    for section in mandatory_sections:
        if section not in str(extracted_data.get("sections", [])).lower():
            structure_penalty += 0.1
            
    return round(max(0.1, length_score - structure_penalty), 2)

def calculate_gap_confidence(gap_type: str, evidence_score: float, heuristic_signal: bool) -> float:
    """
    Formula: (Evidence Verification Score * 0.7) + (Heuristic Signal * 0.3)
    """
    signal_weight = 0.3 if heuristic_signal else 0.0
    return round((evidence_score * 0.7) + signal_weight, 2)

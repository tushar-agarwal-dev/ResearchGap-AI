import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

ALGORITHMS = [
    "cnn", "resnet", "transformer", "bert", "random forest", 
    "svm", "lstm", "vit", "xgboost", "naive bayes", "logistic regression",
    "attention", "mixture of experts", "moe", "diffusion", "gan"
]
DATASETS = [
    "cifar-10", "imagenet", "mnist", "coco", "squad", "uci", "kinetics", "glue", "superglue"
]

def _search_first(pattern: str, text: str, flags: int = 0, default: str = "") -> str:
    match = re.search(pattern, text, flags)
    if match:
        try:
            return match.group(1).strip()
        except IndexError:
            return match.group(0).strip()
    return default

def extract_metadata(text: str) -> Dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = lines[0] if lines else "Unknown Title"
    
    abstract = _search_first(
        r"abstract[:\s]*(.*?)(?:\n\s*\n|\nintroduction|\n1[\.\s])",
        text,
        flags=re.IGNORECASE | re.DOTALL,
        default="",
    )
    
    year = _search_first(r"\b((?:19|20)\d{2})\b", text, flags=re.IGNORECASE, default="")
    
    return {
        "title": title,
        "abstract": abstract[:1200],
        "publication_year": year,
    }

def heuristic_research_audit(text: str) -> Dict[str, Any]:
    """
    High-fidelity deterministic research extractor.
    Identifies real data without calling any external AI.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    patterns = {
        "contributions": [
            r"(?:we propose|we introduce|our contribution|we present|this paper develops)\s+([^.]+)",
            r"(?:novel|new)\s+([^.]+ architecture|[^.]+ method|[^.]+ approach|[^.]+ dataset)",
            r"(?:outperforms|achieves state-of-the-art|best performance)\s+([^.]+)"
        ],
        "gaps": [
            r"(?:future work|future research)\s+([^.]+)",
            r"(?:remains a challenge|is still an open problem|lack of)\s+([^.]+)",
            r"(?:unresolved|not yet explored|beyond the scope)\s+([^.]+)"
        ],
        "limitations": [
            r"(?:limited by|limitation|constraint|weakness)\s+([^.]+)",
            r"(?:does not evaluate|failed to|unable to|narrow scope)\s+([^.]+)",
            r"(?:computationally expensive|high overhead|scalability issues)\s+([^.]+)"
        ],
        "strengths": [
            r"(?:experimental results demonstrate|we show that|evaluated on)\s+([^.]+)",
            r"(?:robust|efficient|scalable|reproducible)\s+([^.]+)",
            r"(?:significant improvement|consistent gains)\s+([^.]+)"
        ]
    }
    
    results = {k: [] for k in patterns.keys()}
    
    # Process sentences for each category
    for s in sentences:
        s_clean = s.strip().replace("\n", " ")
        if len(s_clean) < 40 or len(s_clean) > 500:
            continue
            
        for key, p_list in patterns.items():
            if len(results[key]) >= 3: continue # Cap at 3 per section
            for p in p_list:
                match = re.search(p, s_clean, re.I)
                if match:
                    results[key].append({
                        "text": match.group(1).strip() if len(match.groups()) > 0 else s_clean[:100],
                        "evidence": s_clean,
                        "source_section": "Text Analysis",
                        "confidence": 0.6,
                        "reasoning": "Direct keyword match detected in paper text."
                    })
                    break

    # Extract structured results
    metrics = {}
    metric_patterns = {
        "accuracy": r"accuracy[^0-9]{0,20}([0-9]+(?:\.[0-9]+)?%?)",
        "f1": r"f1(?:-score)?\s*(?:of|is)?\s*([0-9]+(?:\.[0-9]+)?%?)",
        "latency": r"latency\s*(?:of|is)?\s*([0-9]+(?:\.[0-9]+)?\s*ms)",
    }
    for k, p in metric_patterns.items():
        val = _search_first(p, text, re.I)
        if val: metrics[k] = val

    return {
        "contributions": results["contributions"],
        "gaps": results["gaps"],
        "limitations": results["limitations"],
        "strengths": results["strengths"],
        "metrics": metrics,
        "datasets": sorted(list(set([d for d in DATASETS if d in text.lower()])))
    }

def extract_all_insights(text: str) -> Dict[str, Any]:
    metadata = extract_metadata(text)
    audit = heuristic_research_audit(text)
    
    return {
        "metadata": metadata,
        "algorithms": sorted(list(set([a for a in ALGORITHMS if a in text.lower()]))),
        "datasets": audit["datasets"],
        "results": {"metrics": audit["metrics"]},
        "strengths": [s["text"] for s in audit["strengths"]],
        "weaknesses": [l["text"] for l in audit["limitations"]],
        "heuristic_audit": audit, # Pass full audit for fallback
        "domain": "Computer Science" if "algorithm" in text.lower() or "network" in text.lower() else "General Research",
        "complexity": "Advanced" if len(text.split()) > 8000 else "Basic",
        "reading_time": max(5, len(text.split()) // 200)
    }

SECTIONS_MAP = {
    "abstract": [r"abstract"],
    "introduction": [r"introduction", r"background"],
    "methodology": [r"methodology", r"methods", r"proposed approach"],
    "results": [r"results", r"discussion", r"analysis"],
    "limitations": [r"limitations", r"threats to validity"],
    "conclusion": [r"conclusion", r"concluding remarks"],
    "future_work": [r"future work", r"future directions"]
}

def partition_sections(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    sections_content = {k: "" for k in SECTIONS_MAP.keys()}
    sections_content["other"] = ""
    current_section = "other"
    
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        found_header = False
        for sec_name, keywords in SECTIONS_MAP.items():
            if any(re.search(rf"^(?:\d+\.?\s*)?{kw}$", stripped, re.IGNORECASE) for kw in keywords):
                current_section = sec_name
                found_header = True
                break
        if not found_header:
            sections_content[current_section] += line + "\n"
            
    return sections_content

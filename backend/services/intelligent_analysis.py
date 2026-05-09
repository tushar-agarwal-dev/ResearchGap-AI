import math
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, Set

STOPWORDS: Set[str] = {
    "the", "and", "for", "that", "with", "this", "from", "are", "was", "were",
    "have", "has", "had", "into", "their", "about", "using", "use", "used",
    "between", "these", "those", "such", "than", "then", "also", "can", "may",
    "our", "your", "paper", "research", "method", "methods", "result", "results",
}

ALGO_BUCKETS: Dict[str, Set[str]] = {
    "traditional_ml": {"svm", "random forest", "xgboost", "naive bayes", "logistic regression"},
    "deep_learning": {"cnn", "rnn", "lstm", "transformer", "bert", "resnet", "vit"},
}


def tokenize(text: str) -> List[str]:
    """Tokenize text and remove stopwords."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", text.lower())
    return [word for word in words if word not in STOPWORDS]


def keyword_frequency(texts: List[str], top_n: int = 30) -> List[Dict[str, Any]]:
    """Compute keyword frequency across multiple texts."""
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))
    total = sum(counter.values()) or 1
    top = counter.most_common(top_n)
    return [
        {
            "keyword": keyword,
            "count": count,
            "frequency": round(count / total, 4),
        }
        for keyword, count in top
    ]


def trending_topics_by_year(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze top topics grouped by publication year with normalized weights."""
    bucket = defaultdict(Counter)
    year_totals = Counter()
    
    for paper in papers:
        year = str(paper.get("year") or "unknown")
        full_text = paper.get("complete_text") or ""
        tokens = tokenize(full_text)
        bucket[year].update(tokens)
        year_totals[year] += len(tokens) or 1

    trends = []
    for year, counter in sorted(bucket.items(), key=lambda item: item[0]):
        total_tokens = year_totals[year]
        trends.append(
            {
                "year": year,
                "top_topics": [
                    {
                        "keyword": key, 
                        "count": value,
                        "normalized_weight": round(value / total_tokens, 6)
                    } 
                    for key, value in counter.most_common(8)
                ],
            }
        )
    return trends


def detect_research_shifts(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect shifts in methodology over time using percentage growth (Mandate 6)."""
    year_counts = defaultdict(lambda: defaultdict(int))
    year_paper_totals = Counter()
    
    for paper in papers:
        year = str(paper.get("year") or "unknown")
        year_paper_totals[year] += 1
        algos = [item.lower() for item in (paper.get("algorithms") or [])]
        for algo in algos:
            for bucket_name, bucket_algos in ALGO_BUCKETS.items():
                if algo in bucket_algos:
                    year_counts[year][bucket_name] += 1

    sorted_years = sorted([year for year in year_counts if year != "unknown"])
    shifts = []
    for idx in range(1, len(sorted_years)):
        prev_year = sorted_years[idx - 1]
        curr_year = sorted_years[idx]
        
        for bucket_name in ALGO_BUCKETS:
            # Normalize by total papers per year
            prev_norm = year_counts[prev_year][bucket_name] / max(1, year_paper_totals[prev_year])
            curr_norm = year_counts[curr_year][bucket_name] / max(1, year_paper_totals[curr_year])
            
            if prev_norm == 0:
                growth = 1.0 if curr_norm > 0 else 0.0
            else:
                growth = (curr_norm - prev_norm) / prev_norm
            
            if growth == 0:
                continue
                
            direction = "increasing" if growth > 0 else "decreasing"
            shifts.append(
                {
                    "trend": f"{bucket_name} usage {direction}",
                    "from_year": prev_year,
                    "to_year": curr_year,
                    "percentage_growth": round(growth * 100, 2),
                    "confidence": 0.8 # Static confidence for trend heuristic
                }
            )
    return shifts


def detect_research_gaps(papers: List[Dict[str, Any]]) -> List[str]:
    """Heuristic-based research gap detection."""
    # This is a legacy helper, main logic moved to gap_engine.py
    # but we'll keep it for the dashboard with basic checks.
    all_datasets = [item.lower() for paper in papers for item in (paper.get("datasets") or [])]
    text_blob = " ".join((paper.get("complete_text") or "").lower() for paper in papers)
    gaps = []

    if "indian" not in text_blob and "india" not in text_blob:
        gaps.append("Missing Evaluation: India-specific dataset benchmarking.")
    if "multilingual" not in text_blob and "low-resource" not in text_blob:
        gaps.append("Underrepresented Domain: Low-resource language research.")
    
    if all_datasets:
        dataset_counter = Counter(all_datasets)
        top_dataset, top_count = dataset_counter.most_common(1)[0]
        if top_count / max(1, len(all_datasets)) > 0.35:
            gaps.append(f"Underrepresented Domain: Lack of dataset diversity ({top_dataset} dominates).")

    return gaps


def _vectorize(text: str) -> Tuple[Counter, float]:
    """Helper to vectorize text using word counts and compute magnitude."""
    counts = Counter(tokenize(text))
    magnitude = math.sqrt(sum(value * value for value in counts.values())) or 1.0
    return counts, magnitude


def cosine_similarity(text_a: str, text_b: str) -> Tuple[float, float]:
    """Compute cosine similarity and a similarity confidence score (Mandate 4)."""
    vec_a, mag_a = _vectorize(text_a)
    vec_b, mag_b = _vectorize(text_b)
    
    shared_keys = set(vec_a).intersection(vec_b)
    dot = sum(vec_a[key] * vec_b[key] for key in shared_keys)
    
    similarity = dot / (mag_a * mag_b)
    # Confidence based on overlap density
    confidence = min(1.0, len(shared_keys) / max(1, (len(vec_a) + len(vec_b)) / 4))
    
    return round(similarity, 4), round(confidence, 4)


def paper_similarity_matrix(papers: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
    """Generate a matrix of paper similarities."""
    pairs = []
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
            paper_a = papers[i]
            paper_b = papers[j]
            score, conf = cosine_similarity(
                paper_a.get("complete_text", ""), 
                paper_b.get("complete_text", "")
            )
            pairs.append(
                {
                    "paper_a_id": paper_a["id"],
                    "paper_a_name": paper_a["filename"],
                    "paper_b_id": paper_b["id"],
                    "paper_b_name": paper_b["filename"],
                    "similarity": score,
                    "confidence": conf
                }
            )
    pairs.sort(key=lambda item: item["similarity"], reverse=True)
    return pairs[:top_k]


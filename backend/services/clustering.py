import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any
from .semantic_search import _get_model


def cluster_papers(papers: List[Dict[str, Any]], num_clusters: int = 5):
    if not papers:
        # Synthetic Demo Output
        return [{
            "cluster_id": 0,
            "papers": [{"id": 0, "filename": "Baseline Paper"}]
        }]

    if len(papers) < num_clusters:
        num_clusters = max(1, len(papers))
    
    texts = [p["complete_text"] for p in papers]
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)
    
    clusters = []
    for i in range(num_clusters):
        cluster_papers_list = [
            {
                "id": papers[j]["id"],
                "filename": papers[j]["filename"]
            }
            for j in range(len(papers)) if labels[j] == i
        ]
        if cluster_papers_list:
            clusters.append({
                "cluster_id": i,
                "papers": cluster_papers_list
            })
            
    return clusters

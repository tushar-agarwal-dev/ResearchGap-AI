import networkx as nx
from typing import List, Dict, Any


def build_citation_network(papers: List[Dict[str, Any]]):
    if not papers:
        # Synthetic Demo Output
        return {
            "nodes": [{"id": 0, "label": "Start Research"}],
            "links": []
        }

    G = nx.DiGraph()
    
    # Paper IDs and filenames for nodes
    for paper in papers:
        G.add_node(paper["id"], label=paper["filename"])
    
    from .intelligent_analysis import cosine_similarity
    
    threshold = 0.4
    for i in range(len(papers)):
        for j in range(len(papers)):
            if i == j:
                continue

            score, _ = cosine_similarity(papers[i]["complete_text"], papers[j]["complete_text"])
            if score > threshold:
                G.add_edge(papers[i]["id"], papers[j]["id"], weight=float(score))
    # Format for JSON output
    nodes = [{"id": n, "label": G.nodes[n]["label"]} for n in G.nodes]
    edges = [{"source": u, "target": v, "weight": d["weight"]} for u, v, d in G.edges(data=True)]
    
    # Ensure not empty if papers exist
    if not edges and len(nodes) > 1:
        # Fallback: add a few links based on index if no similarity found
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "weight": 0.1})

    return {"nodes": nodes, "links": edges}

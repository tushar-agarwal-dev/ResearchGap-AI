from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Any
import hashlib
import json
import os

_model = None


class MockModel:
    def encode(self, texts, convert_to_numpy=True):
        if isinstance(texts, str):
            texts = [texts]
        # Return random embeddings of the correct dimension
        return np.random.rand(len(texts), 384).astype(np.float32)


def _get_model():
    global _model
    if _model is None:
        # Using a small, efficient model for local development
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer (offline?). Using mock model. Error: {e}")
            _model = MockModel()
    return _model


class SemanticSearchService:
    def __init__(self):
        self.model = _get_model()
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.paper_ids = []
        self.cache_dir = ".embedding_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, text: str) -> str:
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.npy")

    def build_index(self, papers: List[Dict[str, Any]]):
        if not papers:
            return
        
        self.paper_ids = [p["id"] for p in papers]
        embeddings = []
        
        for p in papers:
            text = p["complete_text"]
            cache_path = self._get_cache_path(text)
            
            if os.path.exists(cache_path):
                emb = np.load(cache_path)
            else:
                emb = self.model.encode(text, convert_to_numpy=True)
                np.save(cache_path, emb)
                
            embeddings.append(emb)
            
        embeddings_np = np.vstack(embeddings)
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_np.astype("float32"))

    def _expand_query(self, query: str) -> List[str]:
        # Basic rule-based expansion
        expansions = [query]
        lowered = query.lower()
        if "deep learning" in lowered:
            expansions.append(query.replace("deep learning", "neural networks"))
        if "llm" in lowered:
            expansions.append(query.replace("llm", "large language model"))
        return expansions

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if self.index is None or self.index.ntotal == 0:
            return []

        expanded_queries = self._expand_query(query)
        query_embeddings = self.model.encode(expanded_queries, convert_to_numpy=True)
        
        # Average the embeddings for expanded queries to act as a single robust query vector
        avg_query_embedding = np.mean(query_embeddings, axis=0, keepdims=True)

        distances, indices = self.index.search(avg_query_embedding.astype("float32"), limit)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            
            # Improved score normalization
            dist = distances[0][i]
            score = float(np.exp(-dist / 10.0)) # softmax-like normalization
            
            results.append({
                "paper_id": self.paper_ids[idx],
                "score": score
            })
        
        # Sort by score descending (reranking step)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results

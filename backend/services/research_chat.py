from typing import List, Dict, Any
from .llm_provider import llm_provider
from .semantic_search import SemanticSearchService
import json

search_service = SemanticSearchService()

class ConversationalResearchAssistant:
    def __init__(self):
        self.session_memory = []

    def ask_question(self, query: str, context_papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_papers:
            return {
                "answer": "I don't have any papers in my database to reference yet.",
                "supporting_papers": [],
                "reasoning": "The user corpus is currently empty."
            }

        # RAG Logic: FAISS Retrieval
        search_service.build_index(context_papers)
        matches = search_service.search(query, limit=3)
        
        context_str = ""
        supporting_ids = []
        for m in matches:
            paper = next((p for p in context_papers if p["id"] == m["paper_id"]), None)
            if paper:
                context_str += f"--- Paper [{paper['id']}] ({paper['filename']}) ---\n{paper.get('complete_text', '')[:1000]}\n\n"
                supporting_ids.append(paper["id"])
                
        history = "\n".join(self.session_memory[-3:])

        prompt = f"""
        Answer the following research question based strictly on the provided context.
        Return ONLY a JSON object.
        
        Context:
        {context_str}
        
        History:
        {history}
        
        Question: {query}
        
        JSON Structure:
        {{
          "answer": "direct answer with citations like [ID]",
          "supporting_papers": [list of IDs],
          "reasoning": "detailed academic reasoning trace"
        }}
        """
        
        ai_raw = llm_provider.generate(prompt, "You are a professional academic research assistant.")
        
        try:
            clean_json = ai_raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
            self.session_memory.append(f"User: {query}\nAssistant: {result.get('answer')}")
            return result
        except Exception as e:
            return {
                "answer": ai_raw[:300],
                "supporting_papers": supporting_ids,
                "reasoning": "Standard answer generated; deep reasoning trace failed to parse as JSON."
            }

research_assistant = ConversationalResearchAssistant()

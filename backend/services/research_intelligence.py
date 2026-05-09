import json
import re
import logging
from typing import List, Dict, Any, Optional
from .llm_provider import llm_provider
from .semantic_chunker import semantic_chunking

logger = logging.getLogger(__name__)

class ResearchIntelligenceEngine:
    """
    Consolidated AI Reasoning Pipeline with Deep Heuristic Fallback.
    Mandate: Provide real, grounded insights every time, using AI when possible and NLP heuristics when not.
    """

    def generate_full_report(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        text = paper_data.get("complete_text", "")
        insights = paper_data.get("insights", {})
        
        logger.info(f"Pipeline Trace: Starting Zero-Failure Audit for Paper ID: {paper_data.get('id')}")
        
        if not text.strip():
            return self._heuristic_report(paper_data) # Force fallback even for no text

        # 1. High-Signal Context Assembly
        chunks = semantic_chunking(text)
        sections_map = {}
        for c in chunks:
            sec = c["section"].lower()
            sections_map[sec] = sections_map.get(sec, "") + c["text"] + "\n"

        high_signal_text = (
            sections_map.get("abstract", "") + "\n" +
            sections_map.get("introduction", "") + "\n" +
            sections_map.get("methodology", "") + "\n" +
            sections_map.get("results", "") + "\n" +
            sections_map.get("conclusion", "")
        )
        
        if len(high_signal_text) < 2000:
             high_signal_text = text[:15000]
        else:
             high_signal_text = high_signal_text[:20000]

        # 2. Dual-Track reasoning: Try LLM Track
        report_data = None
        try:
            logger.info("Pipeline Trace: Requesting Comprehensive Research Audit (LLM Track)...")
            report_data = self._request_comprehensive_audit(high_signal_text)
        except Exception as e:
            logger.error(f"LLM Track failed: {e}")

        # 3. Fallback to Heuristic Track if LLM fails
        if not report_data:
            logger.warning("Pipeline Trace: LLM failed. Switching to High-Fidelity Heuristic Track.")
            return self._heuristic_report(paper_data)

        # 4. Final Synthesis & Scoring
        logger.info("Pipeline Trace: LLM Audit successful. Finalizing insights...")
        
        contributions = self._enforce_list(report_data.get("key_contributions", []))
        gaps = self._enforce_list(report_data.get("research_gaps", []))
        strengths = self._enforce_list(report_data.get("strengths", []))
        limitations = self._enforce_list(report_data.get("limitations", []))
        future_directions = self._enforce_list(report_data.get("future_directions", []))

        reliability = self._compute_reliability(paper_data, strengths, limitations)
        recommendation = self._compute_recommendation(contributions, limitations, strengths, paper_data)
        
        evidence_map = self._build_evidence_map([contributions, gaps, strengths, limitations, future_directions])

        # Map to unified schema
        return {
            "problem_statement": report_data.get("problem_statement", ""),
            "primary_objective": report_data.get("primary_objective", ""),
            "executive_summary": {
                "ultra_short_summary": report_data.get("ultra_short_summary", ""),
                "problem_statement": report_data.get("problem_statement", ""),
                "primary_objective": report_data.get("primary_objective", ""),
                "domain_category": report_data.get("domain_category", insights.get("domain", "General"))
            },
            "contributions": contributions,
            "research_gaps": gaps,
            "strengths": strengths,
            "limitations": limitations,
            "future_directions": future_directions,
            "methodology": report_data.get("methodology_summary", "N/A"),
            "datasets": report_data.get("detected_datasets", []),
            "results": report_data.get("detected_results", []),
            "recommendation": recommendation,
            "reliability": reliability,
            "should_read_this": recommendation.get("should_read_this", False),
            "evidence_map": evidence_map,
            "novelty_score": recommendation.get("novelty_score", 0),
            "confidence": recommendation.get("confidence", 0)
        }

    def _request_comprehensive_audit(self, context: str) -> Optional[Dict[str, Any]]:
        prompt = f"""As a Senior Academic Research Analyst, perform a comprehensive audit of the following paper text.
        Return strictly valid JSON with exact evidence quotes.
        
        JSON SCHEMA:
        {{
          "ultra_short_summary": "...",
          "problem_statement": "...",
          "primary_objective": "...",
          "domain_category": "...",
          "methodology_summary": "...",
          "key_contributions": [{{ "text": "...", "evidence": "Exact quote", "source_section": "...", "confidence": 0.9, "reasoning": "..." }}],
          "research_gaps": [{{ "text": "...", "evidence": "Exact quote or mention", "source_section": "...", "confidence": 0.8, "reasoning": "..." }}],
          "strengths": [{{ "text": "...", "evidence": "Exact quote", "source_section": "...", "confidence": 0.9 }}],
          "limitations": [{{ "text": "...", "evidence": "Exact quote", "source_section": "...", "confidence": 0.8, "reasoning": "..." }}],
          "future_directions": [{{ "text": "...", "evidence": "Exact quote", "source_section": "...", "confidence": 0.8 }}],
          "detected_datasets": [],
          "detected_results": []
        }}

        PAPER TEXT:
        {context}"""
        
        raw = llm_provider.generate(prompt, "Senior Research Auditor")
        return self._safe_json_parse(raw)

    def _heuristic_report(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a complete report using only NLP heuristics."""
        insights = paper_data.get("insights", {})
        audit = insights.get("heuristic_audit", {})
        
        contributions = audit.get("contributions", [])
        gaps = audit.get("gaps", [])
        strengths = audit.get("strengths", [])
        limitations = audit.get("limitations", [])
        
        reliability = self._compute_reliability(paper_data, strengths, limitations)
        recommendation = self._compute_recommendation(contributions, limitations, strengths, paper_data)
        recommendation["explanation"] += " [Heuristic Track Analysis]"
        
        evidence_map = self._build_evidence_map([contributions, gaps, strengths, limitations])

        return {
            "problem_statement": contributions[0]["text"] if contributions else "Insufficient evidence detected in extracted paper text.",
            "primary_objective": "Investigation into paper domain.",
            "executive_summary": {
                "ultra_short_summary": (paper_data.get("insights", {}).get("metadata", {}).get("abstract") or "Research paper summary.")[:150],
                "problem_statement": contributions[0]["text"] if contributions else "Insufficient evidence detected in extracted paper text.",
                "primary_objective": "Experimental evaluation of proposed method.",
                "domain_category": insights.get("domain", "General Research")
            },
            "contributions": contributions,
            "research_gaps": gaps,
            "strengths": strengths,
            "limitations": limitations,
            "future_directions": [],
            "methodology": "Heuristically identified structured approach.",
            "datasets": audit.get("datasets", []),
            "results": audit.get("metrics", {}),
            "recommendation": recommendation,
            "reliability": reliability,
            "should_read_this": recommendation.get("should_read_this", False),
            "evidence_map": evidence_map,
            "novelty_score": recommendation.get("novelty_score", 0),
            "confidence": recommendation.get("confidence", 0)
        }

    def _safe_json_parse(self, raw: str) -> Any:
        try:
            clean = re.sub(r"```json\s?|\s?```", "", raw).strip()
            start = clean.find('{')
            end = clean.rfind('}')
            if start != -1 and end != -1:
                return json.loads(clean[start:end+1])
            return None
        except: return None

    def _enforce_list(self, result: Any) -> List[Dict[str, Any]]:
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict) and "text" in item]
        return []

    def _compute_reliability(self, paper_data: Dict[str, Any], strengths: List[Dict], limitations: List[Dict]) -> Dict[str, Any]:
        text = paper_data.get("complete_text", "").lower()
        has_repro = "github.com" in text or "reproduc" in text or "code" in text
        score = 0.5
        if has_repro: score += 0.2
        if len(strengths) > 1: score += 0.2
        final_score = max(0.1, min(1.0, score - (len(limitations) * 0.05)))
        return {
            "score": round(final_score, 2),
            "signals": { "reproducibility": has_repro, "rigor": len(strengths) > 0, "limitation_aware": len(limitations) > 0 }
        }

    def _compute_recommendation(self, contributions: List[Dict], limitations: List[Dict], strengths: List[Dict], paper_data: Dict[str, Any]) -> Dict[str, Any]:
        nov_score = sum(c.get("confidence", 0.5) for c in contributions) / max(1, len(contributions))
        rig_score = sum(s.get("confidence", 0.5) for s in strengths) / max(1, len(strengths))
        penalty = len(limitations) * 5
        final_score = int(max(0, min(100, (nov_score * 50 + rig_score * 50) * 100 / 100 - penalty)))
        
        if not contributions and not strengths:
            final_score = 0
            explanation = "Insufficient evidence detected in extracted paper text."
        else:
            explanation = f"Recommended score of {final_score}/100 based on {len(contributions)} contributions and {len(strengths)} strengths."
            
        return {
            "read_score": final_score,
            "explanation": explanation,
            "should_read_this": final_score > 55,
            "novelty_score": round(nov_score, 2),
            "confidence": round(rig_score, 2)
        }

    def _build_evidence_map(self, insight_lists: List[List[Dict]]) -> List[Dict]:
        evidence_map = []
        for lst in insight_lists:
            for item in lst:
                if isinstance(item, dict) and item.get("evidence"):
                    evidence_map.append(item)
        return evidence_map

    def _empty_report(self, reason: str, paper_data: Dict[str, Any] = None) -> Dict[str, Any]:
        return self._heuristic_report(paper_data)

research_intelligence = ResearchIntelligenceEngine()

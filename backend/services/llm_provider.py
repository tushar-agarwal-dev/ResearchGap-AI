import logging
import os
import time
import json
from typing import Optional
from google import genai
from google.genai import types

from config import settings

logger = logging.getLogger(__name__)

DEBUG_DIR = "debug_logs"

def _save_debug_info(prompt: str, raw_response: str, role: str, status: str = "success"):
    """Saves raw interaction for debugging with timestamps."""
    try:
        debug_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", DEBUG_DIR)
        if not os.path.exists(debug_path):
            os.makedirs(debug_path, exist_ok=True)
            
        timestamp = int(time.time())
        filename = f"{timestamp}_{role.replace(' ', '_')}_{status}.json"
        full_path = os.path.join(debug_path, filename)
        
        with open(full_path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "role": role,
                "status": status,
                "prompt": prompt,
                "raw_response": raw_response
            }, f, indent=2)
            
        logger.info(f"Debug info saved to {full_path}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {e}")

def _get_gemini_client():
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini client successfully initialized.")
            return client
        except Exception as e:
            logger.error(f"CRITICAL: Failed to initialize Gemini client: {e}")
            return None
    logger.error("CRITICAL: GEMINI_API_KEY not found in settings.")
    return None


class LLMProvider:
    def __init__(self):
        self.client = _get_gemini_client()
        self.model_name = settings.GEMINI_MODEL

    def generate(self, prompt: str, role: str = "Assistant", retries: int = 3) -> str:
        logger.info(f"Gemini request started ({role}). Prompt length: {len(prompt)} chars.")
        
        if not self.client:
            reason = "Client not initialized"
            return self._fallback_generate(prompt, reason)
            
        for attempt in range(retries):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=f"You are a {role}.",
                    temperature=0.1 # Very low for deterministic JSON
                )
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                
                if response and response.text:
                    logger.info(f"Gemini response received on attempt {attempt+1}.")
                    _save_debug_info(prompt, response.text, role, "success")
                    return response.text
                
                logger.warning(f"Empty response on attempt {attempt+1}. Retrying...")
                
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Gemini error on attempt {attempt+1}: {err_msg}")
                
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                
                if "400" in err_msg or "INVALID_ARGUMENT" in err_msg:
                    _save_debug_info(prompt, err_msg, role, "error_invalid")
                    break
                
                time.sleep(1)

        reason = f"Exhausted {retries} retries or encountered fatal error."
        _save_debug_info(prompt, reason, role, "failed")
        return self._fallback_generate(prompt, reason)

    def _fallback_generate(self, prompt: str, reason: str) -> str:
        logger.warning(f"Gemini fallback triggered. Reason: {reason}")
        if "ARRAY" in prompt or "key_contributions" in prompt:
            return "[]"
        return "{}"


llm_provider = LLMProvider()

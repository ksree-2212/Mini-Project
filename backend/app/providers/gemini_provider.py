import os
import json
import logging
import requests
from typing import Optional, Dict, Any
from backend.app.config import settings
from backend.app.providers.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    Google Gemini / AI Studio model provider supporting Gemini 2.0 Flash, 1.5 Flash, 1.5 Pro.
    Allows live LLM translation using Google AI Studio API keys.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        raw_key = api_key or os.getenv("GEMINI_API_KEY") or settings.llm_api_key
        if raw_key:
            self.api_key = raw_key.strip().strip('"').strip("'")
        else:
            self.api_key = ""

        raw_model = model or os.getenv("GEMINI_MODEL") or settings.llm_model
        if not raw_model or raw_model.startswith("gpt"):
            self.model = "gemini-2.0-flash"
        else:
            self.model = raw_model

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> LLMResponse:
        if not self.api_key or self.api_key == "YOUR_COPIED_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY is not configured or contains placeholder value.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 4096
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError(f"No response candidates returned: {data}")

            parts = candidates[0].get("content", {}).get("parts", [])
            content = parts[0].get("text", "") if parts else ""

            usage = data.get("usageMetadata", {})
            return LLMResponse(
                content=content,
                model=self.model,
                prompt_tokens=usage.get("promptTokenCount", 0),
                completion_tokens=usage.get("candidatesTokenCount", 0),
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

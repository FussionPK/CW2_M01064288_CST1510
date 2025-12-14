from __future__ import annotations

import json
from typing import Optional

import google.generativeai as genai
import requests


class AIService:
    """Simple abstraction over different LLM providers."""

    def __init__(self, api_key: str, provider: str = "google", model: Optional[str] = None):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model_name = model

        if self.provider == "google":
            genai.configure(api_key=api_key)
            selected_model = self.model_name or "gemini-2.0-flash"
            self._google_model = genai.GenerativeModel(selected_model)
        elif self.provider in {"xai", "grok"}:
            self._endpoint = "https://api.x.ai/v1/chat/completions"
            self.model_name = self.model_name or "grok-4-latest"
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def generate_response(self, prompt: str) -> str:
        """Generate response from the configured provider."""
        if self.provider == "google":
            response = self._google_model.generate_content(prompt)
            return getattr(response, "text", "")

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful analyst assistant."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(self._endpoint, headers=headers, data=json.dumps(payload), timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise RuntimeError(f"x.ai API error: {error.response.text}") from error
        content = response.json()
        choices = content.get("choices", [])
        if not choices:
            raise RuntimeError("No response returned from x.ai API")
        return choices[0]["message"].get("content", "")
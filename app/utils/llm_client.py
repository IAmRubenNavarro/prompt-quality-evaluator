import os
import requests
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
        def __init__(self):
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.anthropic_model = os.getenv("ANTHROPIC_LLM_MODEL")
            self.google_model = os.getenv("GOOGLE_LLM_MODEL")
            self.openai_model = os.getenv("OPENAI_LLM_MODEL")
            self.base_url = os.getenv("OPENROUTER_BASE_URL")

            if not self.api_key or not self.anthropic_model or not self.google_model or not self.openai_model:
                raise ValueError("Unable to fetch environment variable")

        def chat(self, prompt: str, model: str) -> str:
            """Sends a prompt to OpenRouter and returns the text response."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Use chat/completions endpoint for all models
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"

            if "google" in model:
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ]
                }
            elif "anthropic" in model or "openai" in model:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            else:
                raise ValueError("Payload failed to configure")

            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Unified response parsing
            return data["choices"][0]["message"]["content"]
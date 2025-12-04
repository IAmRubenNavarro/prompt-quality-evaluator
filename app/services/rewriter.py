from pathlib import Path
from re import A
from app.utils.llm_client import OpenRouterClient
from src.llm.models import SUPPORTED_MODELS

client = OpenRouterClient()

class RewriterService:
    def __init__(self):
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "rewrite_prompt.txt"
        self.template = prompt_path.read_text()

    def rewrite(self, user_prompt: str) -> str:
        final_prompt = f"{self.template}\n\nUser prompt:\n{user_prompt}"

        response = client.chat(final_prompt, SUPPORTED_MODELS[1])

        return response.strip()
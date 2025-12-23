from pathlib import Path
from app.utils.llm_client import OpenRouterClient

class RewriterService:
    def __init__(self):
        self.client = OpenRouterClient()
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "rewrite_prompt.txt"
        self.template = prompt_path.read_text()

    def rewrite(self, user_prompt: str, model: str = "anthropic") -> str:
        final_prompt = f"{self.template}\n\nUser prompt:\n{user_prompt}"

        # Select model based on provider
        if model == "anthropic":
            selected_model = self.client.anthropic_model
        elif model == "google":
            selected_model = self.client.google_model
        elif model == "openai":
            selected_model = self.client.openai_model
        else:
            selected_model = self.client.anthropic_model

        response = self.client.chat(final_prompt, selected_model)

        return response.strip()
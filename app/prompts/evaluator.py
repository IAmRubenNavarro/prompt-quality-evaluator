import json
from pathlib import Path
from app.utils.llm_client import OpenRouterClient

class EvaluatorServer:
    def __init__(self):
        self.client = OpenRouterClient()
        self.template_path = Path("app/prompts/evaluator_prompt.txt")

    def load_template(self) -> str:
        return self.template_path.read_text()

    def build_prompt(self, user_prompt: str) -> str:
        template = self.load_template()

        return template.replace("{{prompt}}", user_prompt)

    def evaluate(self, user_prompt: str) -> dict:
        composed_prompt = self.build_prompt(user_prompt)
        response_text = self.client.chat(composed_prompt)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError("LLM returned invalid JSON. Response:\n" + response_text)
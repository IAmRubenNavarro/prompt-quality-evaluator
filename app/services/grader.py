import json
from pathlib import Path
from app.utils.llm_client import OpenRouterClient

class GraderService:
    def __init__(self):
        self.client = OpenRouterClient()
        # Use paths relative to this file to avoid working directory issues
        base_path = Path(__file__).parent.parent.parent
        self.template_path = base_path / "app" / "prompts" / "grading_prompt.txt"
        self.rubric_path = base_path / "src" / "grader" / "rubric.json"

        self.rubric = json.loads(self.rubric_path.read_text())

    def load_template(self) -> str: 
        return self.template_path.read_text()

    def build_prompt(self, expected: str, actual: str) -> str:
        template = self.load_template()
        rubric_text = json.dumps(self.rubric["criteria"], indent = 2)

        prompt = template.replace("{{rubric}}", rubric_text)
        prompt = prompt.replace("{{expected}}", expected)
        prompt = prompt.replace("{{actual}}", actual)
        prompt = prompt.replace("{{scale_min}}", str(self.rubric["scoring"]["scale_min"]))
        prompt = prompt.replace("{{scale_max}}", str(self.rubric["scoring"]["scale_max"]))

        return prompt

    def grade(self, expected: str, actual: str) -> dict:
        composed_prompt = self.build_prompt(expected, actual)
        response_text = self.client.chat(composed_prompt, self.client.anthropic_model)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON from LLM:\n" + response_text)


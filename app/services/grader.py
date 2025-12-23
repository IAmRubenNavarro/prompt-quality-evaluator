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

    def grade(self, expected: str, actual: str, model: str = "anthropic") -> dict:
        composed_prompt = self.build_prompt(expected, actual)

        # Select model based on provider
        if model == "anthropic":
            selected_model = self.client.anthropic_model
        elif model == "google":
            selected_model = self.client.google_model
        elif model == "openai":
            selected_model = self.client.openai_model
        else:
            selected_model = self.client.anthropic_model

        response_text = self.client.chat(composed_prompt, selected_model)

        # Strip markdown code fences if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON from LLM:\n" + response_text)

    @staticmethod
    def format_grade(grade: dict) -> str:
        """Convert grading JSON to human-readable text."""
        lines = []
        lines.append("PROMPT GRADING RESULTS")
        lines.append("=" * 50)
        lines.append("")

        if "scores" in grade:
            lines.append("SCORES")
            lines.append("-" * 50)
            for criterion, score in grade["scores"].items():
                lines.append(f"{criterion.title()}: {score}")
            lines.append("")

        if "final_score" in grade:
            lines.append("FINAL SCORE")
            lines.append("-" * 50)
            lines.append(str(grade["final_score"]))
            lines.append("")

        if "explanation" in grade:
            lines.append("EXPLANATION")
            lines.append("-" * 50)
            lines.append(grade["explanation"])

        return "\n".join(lines)


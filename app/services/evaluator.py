import json
from pathlib import Path
from app.utils.llm_client import OpenRouterClient

class EvaluatorService:
    def __init__(self):
        self.client = OpenRouterClient()
        self.template_path = Path("app/prompts/evaluator_prompt.txt")

    def load_template(self) -> str:
        return self.template_path.read_text()

    def build_prompt(self, user_prompt: str) -> str:
        template = self.load_template()
        return template.replace("{{prompt}}", user_prompt)

    def evaluate(self, user_prompt: str, model: str = "anthropic") -> dict:
        composed_prompt = self.build_prompt(user_prompt)

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
            raise ValueError("LLM returned invalid JSON. Response:\n" + response_text)

    @staticmethod
    def format_evaluation(evaluation: dict) -> str:
        """Convert evaluation JSON to human-readable text."""
        lines = []
        lines.append("PROMPT EVALUATION")
        lines.append("=" * 50)
        lines.append("")

        if "clarity" in evaluation:
            lines.append("CLARITY")
            lines.append("-" * 50)
            lines.append(evaluation["clarity"])
            lines.append("")

        if "missing_information" in evaluation:
            lines.append("MISSING INFORMATION")
            lines.append("-" * 50)
            lines.append(evaluation["missing_information"])
            lines.append("")

        if "assumptions" in evaluation:
            lines.append("ASSUMPTIONS")
            lines.append("-" * 50)
            lines.append(evaluation["assumptions"])
            lines.append("")

        if "safety_issues" in evaluation:
            lines.append("SAFETY ISSUES")
            lines.append("-" * 50)
            lines.append(evaluation["safety_issues"])
            lines.append("")

        if "overall_feedback" in evaluation:
            lines.append("OVERALL FEEDBACK")
            lines.append("-" * 50)
            lines.append(evaluation["overall_feedback"])

        return "\n".join(lines)
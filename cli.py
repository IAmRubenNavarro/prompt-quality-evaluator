"""
Console CLI for Prompt Quality Evaluator
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def evaluate_prompt(prompt):
    """Evaluate a prompt"""
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate",
            json={"user_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def rewrite_prompt(prompt):
    """Rewrite a prompt"""
    try:
        response = requests.post(
            f"{BASE_URL}/rewrite",
            json={"user_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def grade_prompt(prompt):
    """Grade a prompt"""
    try:
        response = requests.post(
            f"{BASE_URL}/grade",
            json={"user_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print_header("Prompt Quality Evaluator - Console CLI")

    while True:
        print("\nOptions:")
        print("  1. Evaluate a prompt")
        print("  2. Rewrite a prompt")
        print("  3. Grade a prompt")
        print("  4. Full workflow (Evaluate -> Rewrite -> Grade)")
        print("  5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()

        if choice == "5":
            print("\nGoodbye!")
            sys.exit(0)

        if choice not in ["1", "2", "3", "4"]:
            print("Invalid choice. Please select 1-5.")
            continue

        print("\nEnter your prompt (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)

        prompt = "\n".join(lines).strip()

        if not prompt:
            print("Error: Prompt cannot be empty.")
            continue

        if choice == "1":
            print_header("EVALUATION RESULTS")
            result = evaluate_prompt(prompt)
            print(json.dumps(result, indent=2))

        elif choice == "2":
            print_header("REWRITTEN PROMPT")
            result = rewrite_prompt(prompt)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(result.get("rewritten_prompt", result))

        elif choice == "3":
            print_header("GRADING RESULTS")
            result = grade_prompt(prompt)
            print(json.dumps(result, indent=2))

        elif choice == "4":
            # Full workflow
            print_header("STEP 1: EVALUATION")
            eval_result = evaluate_prompt(prompt)
            print(json.dumps(eval_result, indent=2))

            print_header("STEP 2: REWRITE")
            rewrite_result = rewrite_prompt(prompt)
            if "error" in rewrite_result:
                print(f"Error: {rewrite_result['error']}")
                continue

            rewritten_prompt = rewrite_result.get("rewritten_prompt", "")
            print(rewritten_prompt)

            print_header("STEP 3: GRADE REWRITTEN PROMPT")
            grade_result = grade_prompt(rewritten_prompt)
            print(json.dumps(grade_result, indent=2))

if __name__ == "__main__":
    main()

# Prompt Quality Evaluator

A tool for evaluating, grading, and rewriting prompts using LLMs.

## How to Use

### Live Application

The application is deployed and available at:
**https://prompt-quality-app.niceforest-551e4f1a.eastus.azurecontainerapps.io**

### Demo Interface

For a visual demonstration, open `demo.html` in your web browser. The demo provides an interactive interface with three main features:

1. **Rewrite** - Transform basic prompts into detailed, well-structured prompts
2. **Evaluate** - Analyze prompt quality and receive feedback
3. **Grade** - Compare expected vs actual prompts

### API Endpoints

#### Health Check
```bash
curl https://prompt-quality-app.niceforest-551e4f1a.eastus.azurecontainerapps.io/health
```

#### Rewrite a Prompt
```bash
curl -X POST https://prompt-quality-app.niceforest-551e4f1a.eastus.azurecontainerapps.io/rewrite \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Write a function to add two numbers"}'
```

#### Evaluate a Prompt
```bash
curl -X POST https://prompt-quality-app.niceforest-551e4f1a.eastus.azurecontainerapps.io/evaluate \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Write a function to add two numbers"}'
```

#### Grade a Prompt
```bash
curl -X POST https://prompt-quality-app.niceforest-551e4f1a.eastus.azurecontainerapps.io/grade \
  -H "Content-Type: application/json" \
  -d '{"expected": "A detailed prompt", "actual": "Write code"}'
```

### Interactive CLI

Use the command-line interface for local testing:

```bash
python cli.py
```

This provides an interactive menu to:
- Evaluate prompts
- Rewrite prompts
- Grade prompts
- Run the full workflow

## Upcoming Changes

Working on adding clarity for Evaluate and Grading responses. (Removing the JSON response)

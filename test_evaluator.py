from app.services.evaluator import EvaluatorService

svc = EvaluatorService()

result = svc.evaluate("Explain quantum computing to a 10 year old.")
print(result)

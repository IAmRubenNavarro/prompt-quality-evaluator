from app.services.grader import GraderService
from app.services.rewriter import RewriterService

# Test RewriterService
rewriter = RewriterService()

result = rewriter.rewrite(
    "Write a function that calculates fibonacci numbers"
)

print("Rewrite result:")
print(result)
"""
Simple test script for the RewriterService.
This script demonstrates how the rewriter improves prompt quality.
"""

from app.services.grader import GraderService
from app.services.rewriter import RewriterService

# Initialize the rewriter service
rewriter = RewriterService()

# Test the rewriter with a basic prompt
# The rewriter will enhance this simple prompt with better structure and clarity
result = rewriter.rewrite(
    "Write a function that calculates fibonacci numbers"
)

# Display the rewritten prompt
print("Rewrite result:")
print(result)
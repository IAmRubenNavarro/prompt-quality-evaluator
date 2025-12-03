from app.services.grader import GraderService

grader = GraderService()

result = grader.grade(
    expected="19",
    actual="The answer is 19."
)

print(result)
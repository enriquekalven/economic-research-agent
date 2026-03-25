import inspect
from google.adk.runners import InMemoryRunner
print(f"Runner.run signature: {inspect.signature(InMemoryRunner.run)}")

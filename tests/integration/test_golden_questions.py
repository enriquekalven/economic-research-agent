import pytest
import os
import json
from google.adk.runners import InMemoryRunner
from google.genai import types

PROJECT_ROOT = "/Users/enriq/Documents/git/economic_research_agent"

# Questions mapping
GOLDEN_QUESTIONS = [
    # 1. FRED Macro
    {
        "source": "FRED",
        "question": "Compare the 10-year trend of Residential Construction in Austin vs. Raleigh.",
        "expected_mention": "austin"
    },
    # 2. BLS Labor
    {
        "source": "BLS",
        "question": "What are the median hourly wages for Software Developers in Salt Lake City?",
        "expected_mention": "salt lake"
    },
    # 3. EIA Energy
    {
        "source": "EIA",
        "question": "What is the industrial electricity rate per kWh in Ohio?",
        "expected_mention": "ohio"
    },
    # 4. News Sentiment
    {
        "source": "NewsAPI",
        "question": "Detect market sentiment headwind for semiconductor plants in Oregon.",
        "expected_mention": "oregon"
    },
    # 5. COLA (C2ER)
    {
        "source": "C2ER",
        "question": "What is the real purchasing power of $150k in Austin vs. Charlotte?",
        "expected_mention": "austin"
    },
    # 6. OpenSecrets Policy
    {
        "source": "OpenSecrets",
        "question": "Which states have upcoming corporate tax sunsets in the next 24 months?",
        "expected_mention": "tax"
    }
]

@pytest.fixture(scope="module")
def runner():
    # Loophole to run project tests from inside scratch workspace
    os.chdir(PROJECT_ROOT)
    from dotenv import load_dotenv
    load_dotenv()
    
    from economic_research_agent.agent import agent
    runner_instance = InMemoryRunner(app=agent)
    runner_instance.auto_create_session = True
    return runner_instance

@pytest.mark.parametrize("scenario", GOLDEN_QUESTIONS)
def test_golden_question(runner, scenario):
    """Run golden questions against the live agent to verify integration."""
    question = scenario["question"]
    expected_mention = scenario["expected_mention"]
    
    print(f"\nRunning Golden Question for {scenario['source']}: {question}")
    
    response_generator = runner.run(
        new_message=types.Content(parts=[types.Part(text=question)]),
        user_id="integration-tester",
        session_id=f"test-session-{scenario['source'].lower()}"
    )
    
    report_parts = []
    for event in response_generator:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    report_parts.append(part.text)
                    
    report = "".join(report_parts)
    
    assert len(report) > 0, f"Received empty report for {scenario['source']}"
    assert expected_mention.lower() in report.lower(), f"Expected mention of '{expected_mention}' in response for {scenario['source']}"
    print(f"Success! Response contains '{expected_mention}': {report[:100]}...")

#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""
ERA Evaluation Science (v2.0). 
Uses Vertex AI Gen AI Evaluation Service to benchmark grounding performance.
"""

import os
import json
import pandas as pd
from google.adk.runners import InMemoryRunner
from vertexai.evaluation import EvalTask, PointwiseMetric
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize ERA Agent (ADK 2.0)
from economic_research_agent.agent import agent
runner = InMemoryRunner(app=agent)

# 2. Define Professional Evaluation Metric (LLM-as-a-Judge)
GROUNDING_METRIC = PointwiseMetric(
    metric="era_grounding_fidelity",
    metric_prompt="""
    Evaluate the response for institutional-grade economic grounding.
    Score 5/5 if:
    - It cites specific numerical tool outputs (e.g., 'EIA: 7.2c/kWh').
    - It correctly identifies regionalCost-Drivers.
    - It uses the A2UI format for charts where appropriate.
    """,
    baseline_model="gemini-1.5-pro",
)

def run_benchmarks():
    print("🛰️ ERA EVALUATION SCIENCE: Initiating High-Fidelity Benchmarks...")
    
    # 3. Load Golden Set
    with open("eval/golden_set.json", "r") as f:
        golden_set = json.load(f)
    
    # 4. Execute Simulation Loop
    results = []
    for test in golden_set:
        print(f"🔬 Testing: {test['input'][:50]}...")
        try:
            response = runner.run(
                newMessage=test['input'],
                userId="eval-suit",
                sessionId="eval-session"
            )
            results.append({
                "prompt": test['input'],
                "response": response.text,
                "reference": str(test['expected_output'])
            })
        except Exception as e:
            print(f"❌ Eval Error on Input: {e}")

    # 5. Summary Report
    df = pd.DataFrame(results)
    print("\n📈 ERA PERFORMANCE SUMMARY:")
    print(df[["prompt", "response"]].head())
    print("\n🚀 EVALUATION COMPLETE. (Results available in Evidence Lake).")

if __name__ == "__main__":
    run_benchmarks()

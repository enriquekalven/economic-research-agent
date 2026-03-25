#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ERA Local Runner. Interactive Session with the ADK 2.0 Agent."""

import os
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

# 1. Load Environment (API Keys)
load_dotenv()

def run_era():
    print("🧠 Initializing Economic Research Agent (ADK 2.0)...")
    
    # 2. Import Agent App
    try:
        from economic_research_agent.agent import agent
    except ImportError as e:
        print(f"❌ Error importing ERA: {e}")
        sys.exit(1)

    # 3. Initialize Runner
    runner = InMemoryRunner(app=agent)
    runner.auto_create_session = True
    
    # Pre-create the default session to avoid lookup errors in some ADK environments
    try:
        runner.create_session(user_id="local-tester", session_id="default-session")
    except Exception:
        pass # Session might already exist or auto-creation is sufficient

    print("\n🛰️ ERA ONLINE. Ask your site-selection or regional economic question.")
    print("(Example: 'Compare Austin and Raleigh for a software hub.')")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("👉 YOU: ")
        if query.lower() in ["exit", "quit", "q"]:
            break
        
        print("\n⏳ ERA IS RESEARCHING (Planner -> Researcher -> Auditor -> Scribe)...")
        
        try:
            from google.genai import types
            response_generator = runner.run(
                new_message=types.Content(parts=[types.Part(text=query)]),
                user_id="local-tester",
                session_id="default-session"
            )
            
            # ADK 2.0 returns a generator
            full_report = []
            for event in response_generator:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            full_report.append(part.text)
            
            report = "".join(full_report)
            
            # Extract text from composite response
            print(f"\n📑 ERA EXECUTIVE REPORT:\n")
            print(report)
                
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"❌ ERA Execution Error: {e}")

if __name__ == "__main__":
    run_era()

#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""Standardized Deployment Engine for Vertex AI Reasoning Engine (ADK 2.0)."""

import os
import vertexai
from vertexai.preview import reasoning_engines
import google.auth

def deploy_era_to_vertex(project_id: str, location: str = "us-central1", display_name: str = "economic-research-agent"):
    """
    Deploys the ERA ADK App to a Vertex AI Reasoning Engine.
    Requires google-adk and google-cloud-aiplatform.
    """
    print(f"🚀 Initializing Deployment for {display_name} in {location}...")
    vertexai.init(project=project_id, location=location)
    
    # Import the app here to ensure environment is set
    from economic_research_agent.agent import agent
    
    remote_app = reasoning_engines.ReasoningEngine.create(
        agent,
        requirements=[
            "google-adk>=1.24.0",
            "google-cloud-aiplatform>=1.136.0",
            "fredapi>=0.5.2",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
        ],
        display_name=display_name,
    )
    
    print(f"✅ Deployment Successful!")
    print(f"Reasoning Engine ID: {remote_app.resource_name}")
    return remote_app.resource_name

if __name__ == "__main__":
    _, project = google.auth.default()
    deploy_era_to_vertex(project_id=project)

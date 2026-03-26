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
    # Use the discovered staging bucket for Reason Engine serialized assets
    staging_bucket = f"gs://{project_id}-agent-engine-v16"
    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)
    
    # Calculate absolute path for extra_packages
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    agent_package_path = project_root
    
    # Add project root to sys.path to ensure economic_research_agent can be imported
    import sys
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Import the cloud-ready reasoning engine instance
    from economic_research_agent.agent import reasoning_engine
    
    print(f"📦 Packaging from: {agent_package_path}")

    # Read requirements from requirements.txt
    requirements_path = os.path.join(project_root, "requirements.txt")
    with open(requirements_path, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    remote_app = reasoning_engines.ReasoningEngine.create(
        reasoning_engine,
        requirements=requirements,
        display_name=display_name,
        description="Enterprise-grade Economic Research Agent (ERA) for site-selection and macro analytics.",
        extra_packages=[agent_package_path],
    )
    
    print(f"✅ Deployment Successful!")
    print(f"Reasoning Engine ID: {remote_app.resource_name}")
    return remote_app.resource_name

if __name__ == "__main__":
    try:
        _, project = google.auth.default()
        deploy_era_to_vertex(project_id=project or "project-maui")
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")

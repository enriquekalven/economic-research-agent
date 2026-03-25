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
    
    # Import the app here to ensure environment is set
    from economic_research_agent.agent import agent
    
    # Define environment variables to be passed to the Reasoning Engine
    env_vars = {
        "BEA_API_KEY": os.getenv("BEA_API_KEY"),
        "FRED_API_KEY": os.getenv("FRED_API_KEY"),
        "CENSUS_API_KEY": os.getenv("CENSUS_API_KEY"),
        "EIA_API_KEY": os.getenv("EIA_API_KEY"),
        "BLS_API_KEY": os.getenv("BLS_API_KEY"),
        "HUD_API_KEY": os.getenv("HUD_API_KEY"),
        "FEC_API_KEY": os.getenv("FEC_API_KEY"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
    }
    
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
        extra_packages=["economic_research_agent"],
        # Note: ReasonEngine recently started supporting env_vars in some versions,
        # otherwise we ensure they are pickled in the agent's class instance.
    )
    
    print(f"✅ Deployment Successful!")
    print(f"Reasoning Engine ID: {remote_app.resource_name}")
    return remote_app.resource_name

if __name__ == "__main__":
    _, project = google.auth.default()
    deploy_era_to_vertex(project_id=project)

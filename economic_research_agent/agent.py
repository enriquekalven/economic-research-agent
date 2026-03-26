#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""
Economic Research Agent (ERA) - ADK 2.0 Implementation.
Replaces LangChain/LangGraph with native Vertex AI Agent Development Kit.
"""

import os
import json
from typing import List, Optional
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Specialized Skill Imports
from economic_research_agent.tools.bls_skill import (
    labor_force_stats_skill,
    median_hourly_wages_skill,
    state_tax_rate_skill,
    state_union_employment_skill
)
from economic_research_agent.tools.fred_skill import fetch_regional_macro_stats
from economic_research_agent.tools.eia_skill import fetch_state_electricity_rates
from economic_research_agent.tools.real_estate_skill import get_real_estate_roi
from economic_research_agent.tools.talent_pipeline_skill import get_talent_pipeline_roi
from economic_research_agent.tools.census_skill import fetch_census_education_stats
from economic_research_agent.tools.bea_skill import fetch_bea_regional_data
from economic_research_agent.tools.hud_skill import (
    fetch_hud_fmr_data,
    fetch_hud_income_limits,
    analyze_housing_affordability
)
from economic_research_agent.tools.tax_foundation_skill import fetch_state_tax_rates
from economic_research_agent.tools.trade_skill import fetch_regional_trade_data
from economic_research_agent.tools.regulatory_skill import fetch_regulatory_notices
from .prompt import Prompts

prompts = Prompts()
ERA_INSTRUCTIONS = prompts.main_era_instructions()

class ERAAgent:
    agent_framework = "google-adk"

    def __init__(self):
        """Standard container for the Reasoning Engine. State-free to ensure cloud pickling stability."""
        pass

    def get_app(self) -> App:
        """Lazily instantiates the ADK App and Agent only when needed."""
        tools = [
            labor_force_stats_skill,
            median_hourly_wages_skill,
            state_tax_rate_skill,
            state_union_employment_skill,
            fetch_regional_macro_stats,
            fetch_state_electricity_rates,
            get_real_estate_roi,
            get_talent_pipeline_roi,
            fetch_census_education_stats,
            fetch_bea_regional_data,
            fetch_hud_fmr_data,
            fetch_hud_income_limits,
            analyze_housing_affordability,
            fetch_state_tax_rates,
            fetch_regional_trade_data,
            fetch_regulatory_notices,
        ]
        
        era_agent = Agent(
            name="ERA_Consultant",
            model=Gemini(model_name="gemini-2.5-flash"),
            instruction=ERA_INSTRUCTIONS,
            tools=tools,
        )
        return App(root_agent=era_agent, name="Economic_Research_Agent")

    def query(self, input: str) -> str:
        """Standard Reasoning Engine entry point."""
        # Cloud Secrets fallback using Secret Manager
        def get_cloud_secret(key_name):
            val = os.getenv(key_name)
            if val:
                return val
            try:
                from economic_research_agent.shared_libraries.helper import access_secret_version
                # We can hardcode the workshop project-maui for consistency
                return access_secret_version(project_id="project-maui", secret_id=key_name)
            except Exception:
                return None

        # Provision keys in runtime environment
        env_vars = {
            "BEA_API_KEY": get_cloud_secret("BEA_API_KEY"),
            "FRED_API_KEY": get_cloud_secret("FRED_API_KEY"),
            "CENSUS_API_KEY": get_cloud_secret("CENSUS_API_KEY"),
            "EIA_API_KEY": get_cloud_secret("EIA_API_KEY"),
            "BLS_API_KEY": get_cloud_secret("BLS_API_KEY"),
            "HUD_API_KEY": get_cloud_secret("HUD_API_KEY"),
            "FEC_API_KEY": get_cloud_secret("FEC_API_KEY"),
            "NEWS_API_KEY": get_cloud_secret("NEWS_API_KEY"),
            "SERPER_API_KEY": get_cloud_secret("SERPER_API_KEY"),
            "CDC_APP_TOKEN": get_cloud_secret("CDC_APP_TOKEN"),
            "OPENFDA_API_KEY": get_cloud_secret("OPENFDA_API_KEY"),
        }
        for k, v in env_vars.items():
            if v: os.environ[k] = v
        
        # Instantiate App & Runner at runtime rather than deploy-time
        app = self.get_app()
        
        from google.adk.runners import InMemoryRunner
        runner = InMemoryRunner(app=app)
        runner.auto_create_session = True
        
        responses = runner.run(new_message=input)
        full_text = ""
        for res in responses:
            if hasattr(res, 'content') and res.content.parts:
                for part in res.content.parts:
                    if part.text:
                        full_text += part.text

        # ⚖️ Active Actor-Critic Loop (Self-Correction)
        try:
            from .sub_agents.agent import JudgeAgent
            from google.adk.apps import App
            
            judge = JudgeAgent().get_agent()
            judge_app = App(root_agent=judge, name="Judge_Review")
            judge_runner = InMemoryRunner(app=judge_app)
            judge_runner.auto_create_session = True
            
            # Iteration 1: Judge the initial draft
            judge_prompt = (
                "Please audit this draft report. Use Google Search to verify quantitative claims if needed. "
                "If you find contradictions or hallucinations, start your response with '[REJECT]' and explain exactly what to fix."
                f"\n\nDraft:\n{full_text}"
            )
            judge_responses = judge_runner.run(new_message=judge_prompt)
            
            judge_text = ""
            for res in judge_responses:
                if hasattr(res, 'content') and res.content.parts:
                    for part in res.content.parts:
                        if part.text:
                            judge_text += part.text
            
            # If rejected, run Researcher again with the correction context!
            if "[REJECT]" in judge_text:
                print("⚠️ [Actor-Critic] Judge rejected the draft! Self-correcting...")
                correction_prompt = (
                    f"Your previous draft was REJECTED by the Auditor Judge. Please use your tools to FIX the following discrepancies and generate a final report:\n\n"
                    f"### Auditor Feedback:\n{judge_text}\n\n"
                    f"### Previous Draft:\n{full_text}"
                )
                
                # Reset runner or run again
                retry_responses = runner.run(new_message=correction_prompt)
                corrected_text = ""
                for res in retry_responses:
                    if hasattr(res, 'content') and res.content.parts:
                        for part in res.content.parts:
                            if part.text:
                                corrected_text += part.text
                
                return f"{corrected_text}\n\n---\n### ⚖️ Auditor Judge Verification (Self-Corrected v2)\n{judge_text}"
                
            return f"{full_text}\n\n---\n### ⚖️ Auditor Judge Verification (Passed v1)\n{judge_text}"
            
        except Exception as e:
            return f"{full_text}\n\n---\n⚠️ *Judge verification failed: {e}*"

# Export the entry points for different environments
export_agent = ERAAgent()

# Use 'agent' for local runners (Streamlit uses App instance directly)
agent = export_agent.get_app()

# Use 'reasoning_engine' for cloud deployment (Vertex AI expects class with .query() method)
reasoning_engine = export_agent

# Also export root_agent for local CLI usage
root_agent = export_agent.get_app().root_agent

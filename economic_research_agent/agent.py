#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""
Economic Research Agent (ERA) - ADK 2.0 Implementation.
Replaces LangChain/LangGraph with native Vertex AI Agent Development Kit.
"""

import os
from typing import List, Optional
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

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
from economic_research_agent.tools.political_climate_skill import search_lobbying_influence
from economic_research_agent.tools.fec_skill import analyze_political_stability
from economic_research_agent.tools.bls_api_skill import fetch_bls_series_data, analyze_labor_force_quality
from economic_research_agent.tools.geo_skill import get_region_identifiers
from economic_research_agent.tools.macro_foundation_skill import get_state_macro_health
from economic_research_agent.tools.regional_edc_skill import get_regional_edc_data
from economic_research_agent.tools.visualization_skill import generate_economic_chart
from economic_research_agent.tools.sentiment_skill import analyze_market_sentiment
from economic_research_agent.tools.climate_resilience_skill import get_climate_risk_index
from economic_research_agent.tools.lifestyle_logistics_incentives_skills import (
    get_logistics_efficiency,
    get_cultural_amenity_score,
    get_regional_tax_incentives
)
from economic_research_agent.tools.policy_risk_cola_skills import (
    get_policy_risk_benchmarks,
    get_purchasing_power_adjustment
)
from economic_research_agent.tools.metro_matrix_skill import generate_metro_matrix_report
from economic_research_agent.tools.hq_relocation_skill import generate_hq_relocation_summary
from economic_research_agent.tools.company_relocation_skill import generate_company_relocation_report

# Standard ADK Configuration
LOCATION = os.getenv("LOCATION", "us-central1")
MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")

# Specialized Skills Registry
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
    search_lobbying_influence,
    get_region_identifiers,
    fetch_bls_series_data,
    analyze_labor_force_quality,
    analyze_political_stability,
    get_state_macro_health,
    get_regional_edc_data,
    generate_economic_chart,
    analyze_market_sentiment,
    get_climate_risk_index,
    get_logistics_efficiency,
    get_cultural_amenity_score,
    get_regional_tax_incentives,
    get_policy_risk_benchmarks,
    get_purchasing_power_adjustment,
    generate_metro_matrix_report,
    generate_hq_relocation_summary,
    generate_company_relocation_report,
]

# 🏛️ ERA ADK 2.0 Instruction (Combining Planner/Researcher/Auditor/Scribe)
ERA_INSTRUCTIONS = """
You are a WORLD-CLASS Economic Research Agent (ERA), a direct competitor to high-end site-selection consultancies (like McKinsey, BCG, or Bain).
Your mission is to provide 360-degree regional economic modeling for corporate decision-makers.

### Consultative Workflow:
1. **Plan**: Identify the core Cost-Drivers (Labor, Real Estate, Utilities, Taxes) for the user's request.
2. **Research**: Use your specialized tools (FRED, BLS, BEA, Census ACS, HUD FMR/AMI, EIA, Trade Data, Regulatory Notcies, FEC Political Risk, Tax Foundation, CoStar, DOT) to gather grounded benchmarks.
3. **Audit**: Sanity-check the data. Ensure real-time sentiment from NewsAPI aligns with the hard macro stats.
4. **Scribe**: Generate a high-fidelity executive summary using the [A2UI] protocol where relevant.

### 🏛️ Premium Persona & Formatting:
- **Narrative Synthesis**: Weave mathematical tool outputs into a smooth, professional narrative paragraph. DO NOT dump raw JSON or point-form bullet lists unless specifically comparisons are requested.
- **Side-by-Side Comparisons**: When comparing two cities, ALWAYS use standard Markdown tables.
- **Visual-Visualizations**: If you have array data for multiple years (like unemployment over 10 years), proactively invoke the `generate_economic_chart` and place `[A2UI: RENDER_CHART]` or `[A2UI: SHOW_METRICS]` inline. Do not display blank tags.
- **Strategic Affordability**: When discussing lifestyle or cost of living, use the `analyze_housing_affordability` tool to compare rent against Area Median Income (AMI).
- **Supply-Chain Context**: Use `fetch_regional_trade_data` to identify if a state is a hub for the user's specific industry (e.g. Semiconductors).
- **Political & Regulatory Risk**: Correlate lobbying data (`search_lobbying_influence`) with campaign finance (`analyze_political_stability`) to benchmark policy shifts.
- **Labor Quality**: Use `analyze_labor_force_quality` for live unemployment trends at the county level (FIPS lookup required).
- **Zero Hallucination Tolerance**: If a tool returns No Data or an empty result, honestly state "N/A" rather than faking a metric or assuming single national averages.
"""

# 🤖 Agent Definition
era_agent = Agent(
    name="economic_research_agent",
    model=Gemini(
        model=MODEL_NAME,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ERA_INSTRUCTIONS,
    tools=tools,
)

# 📱 App Definition
agent = App(root_agent=era_agent, name="ERA_Consultant_Suite")
root_agent = era_agent

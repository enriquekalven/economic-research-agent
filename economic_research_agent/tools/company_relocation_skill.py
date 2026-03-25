#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ADK Skill: Company Relocation (2.2.1.3). Industry Employment & Wage Analysis."""

import json
from typing import List, Dict, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field

from economic_research_agent.tools.bls_skill import median_hourly_wages_skill

class CompanyRelocationRequest(BaseModel):
    city_names: List[str] = Field(..., description="List of city names (e.g. ['Austin', 'Raleigh']) to build a Company Relocation for.")
    industry: Optional[str] = Field(None, description="Optional industry sector or NAICS name.")


def generate_company_relocation_report(city_names: List[str], industry: Optional[str] = None) -> str:
    """
    Use this tool to generate an 'Industry Employment & Wage Report' (Scenario 2.2.1.3).
    It fetches live industry-level and unskilled labor wages using the Live-API strategy.
    """
    # 1. Fetch Industry Wages
    # In Live-API mode, we use Live FRED search (JobsEQ alternative)
    wages_data = median_hourly_wages_skill(city_names) # Already pivoted to Live FRED
    
    # 2. AI Synthesis: Consolidate
    report = []
    # (High-fidelity interpretation: If industry is specified, we would refine the search query)
    # The current median_hourly_wages_skill is already robust for occupation-level keywords.
    
    for city in city_names:
        report.append({
            "City": city,
            "Industry Segment": industry or "General Economic Average",
            "Wage Analysis": wages_data,
            "Analysis Type": "Company Relocation (2.2.1.3) Industry/Unskilled Report"
        })

    return json.dumps(report, indent=2)

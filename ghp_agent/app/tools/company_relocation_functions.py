#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting Company Relocation workflow."""

import concurrent.futures
import logging
import os
from typing import Any, Dict, List, Tuple

from langchain_core.tools import tool
import pandas as pd

from app.tools.common.jobs_eq import (
    get_empl_and_wages_by_industry,
    get_process_naics_requests,
    get_unskilled_labor_wages,
)


PROJECT_ID = "ghp-poc"
REGION = "us-central1"
DATA_AXLE = "ghp-poc.jobseq.data_axle"
INDUSTRY_2024Q3 = "ghp-poc.jobseq.industry_2024q3_cleaned"
INDUSTRY_OCCUPATION_2024Q3 = "ghp-poc.jobseq.industry_occupation_mix_2024q3"
OCCUPATION_WAGES_2024Q3 = "ghp-poc.jobseq.`jobseq-occupation-wages-2024q3`"
NAICS_US_CODE_2022 = "ghp-poc.jobseq.naics_us_code_2022"

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)  # Change the working directory
filepath = os.path.join(current_dir, "common/naics_mappings.csv")
NAICS_MAPPING = pd.read_csv(filepath)


# Logger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def find_company_relocation(
    metro_areas: List[Dict[str, Any]],
    industry_requests: List[str],
) -> Tuple[pd.DataFrame, set]:
    """Search for company relocation for each specified city.

    Use the user's session to determine if you already know
    the cities the user is looking for.

    Args:
        metro_areas (List[Dict[str, Any]]): A list of dictionaries
            for each metro area the user is looking to get a metro
            matrix for. Minimum dictionaries in this list is 1.
            Each dictionary should follow this schema:
            {{
                "city_name": "",
                "state": "",
                "state_abbreviation": ""
            }}
        industry_requests: A list of strings, where each string is either an 
            industry name or a NAICS code (numerical code), as requested
            by the user (E.g., ["325", "chemical manufacturing", "5555"]).

    Returns:
        empl_and_wages_by_industry_df: A Pandas DataFrame containing the
            employment and wages by industry.
        unskilled_labor_salaries_df: A Pandas Dataframe containing the unskilled
            labor salaries.
    """
    city_names = [f"{area.get('city_name')}" for area in metro_areas]
    found_names, found_codes = get_process_naics_requests(
        naics_requests=industry_requests,
        naics_dataframe=NAICS_MAPPING)
    if not found_names:
        return "Could not find the requested Industry."
    # Parallelize functions for company relocation.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                get_empl_and_wages_by_industry,
                city_names,
                found_codes
            ): "empl_wages",
            executor.submit(
                get_unskilled_labor_wages,
                city_names,
                found_names
            ): "labor_wages",
        }

        results = {}
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    # Get results.
    empl_wages_by_industry= results["empl_wages"]
    unskilled_labor = results["labor_wages"]
    citations = {"citations": "https://jobseq.eqsuite.com/"}
    print(empl_wages_by_industry, unskilled_labor, citations)
    return empl_wages_by_industry, unskilled_labor, citations

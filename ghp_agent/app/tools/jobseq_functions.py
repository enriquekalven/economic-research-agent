#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Tools to support JobsEQ data source."""

from typing import List, Tuple

from langchain_core.tools import tool
import pandas as pd

from app.tools.common.jobs_eq import (
    get_empl_and_wages_by_industry,
    get_process_naics_requests,
    get_unskilled_labor_wages,
)


@tool
def process_naics_requests(
    naics_requests: List[str],
)  -> Tuple[List[str]]:
    """This tool is required to run before calling empl_and_wages_by_industry
    and unskilled_labor_wages tools. It processes a list of strings containing
    NAICS codes and industry names, checking against a Pandas DataFrame and
    returning unique industry names and NAICS codes.

    Args:
        naics_requests: A list of strings, where each string is either an 
            industry name or a NAICS code (numerical code). This is taken
            from the user's request. Every requested code and industry
            should be included.

    Returns:
        A tuple containing two lists:
            - A list of unique industry names.
            - A list of unique NAICS codes.
    """
    # Get NAICS Industry titles and codes from user query.
    industry_names, naics_codes = get_process_naics_requests(
        naics_requests=naics_requests,
    )

    return industry_names, naics_codes


@tool
def empl_and_wages_by_industry(
    city_names: List[str],
    naics_codes: List[str],
)->pd.DataFrame:
    """Use this tool whenever a user is looking for information on employment
    and wages by industry. This might include employment numbers and
    current average annual wages for a given industry.

    Args:
        city_names: List of city's requested by user.
        naics_codes: List of NAICS Codes requested for Industries.
            This comes directly from the process_naics_requests tool.

    Returns:
        Pandas df representing industry employment and wages by industry.
    """
    # Get employment and wages by industry sub sector.
    sector_employment_and_wages_by_sub_sector = get_empl_and_wages_by_industry(
        city_names=city_names,
        naics_codes=naics_codes
    )

    return sector_employment_and_wages_by_sub_sector


@tool
def unskilled_labor_wages(
    city_names: List[str],
    naics_codes: List[str],
    naics_titles: List[str],
)->pd.DataFrame:
    """Use this tool whenever a user is looking for unskilled labor wages
    information. This might include average salary, entry level salary,
    and experienced salary given an occupation, industry, and city.

    Args:
        city_names: List of cities requested by user.
        naics_codes: List of NAICS Codes requested for Industries.
            This comes directly from the process_naics_requests tool.
        naics_titles: List of NAICS Titles requested for Industries.
            This comes directly from the process_naics_requests tool.

    Returns:
        Pandas df representing the unskilled labor salaries by job title table.
    """
    unskilled_labor = get_unskilled_labor_wages(
        city_names=city_names,
        naics_codes=naics_codes,
        naics_titles=naics_titles
    )

    return unskilled_labor

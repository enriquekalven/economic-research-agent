#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting Company Relocation workflow."""

import concurrent.futures
import json
import Levenshtein
import logging
import os
import re
from typing import Any, Dict, List, Tuple

from google.genai import types
from langchain_core.tools import tool
import pandas as pd

from app.tools.common.jobs_eq import (
    extract_naics_info
)
from app.tools.common.gemini_sdk import GeminiSDKManager
from app.utils.helper import (
    join_sets,
    merge_dataframes
)


PROJECT_ID = "ghp-poc"
REGION = "us-central1"
DATA_AXLE = "ghp-poc.jobseq.data_axle"
INDUSTRY_2024Q3 = "ghp-poc.jobseq.industry_2024q3_cleaned"
INDUSTRY_OCCUPATION_2024Q3 = "ghp-poc.jobseq.industry_occupation_mix_2024q3"
OCCUPATION_WAGES_2024Q3 = "ghp-poc.jobseq.`jobseq-occupation-wages-2024q3`"

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
    user_query: str,
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
        user_query: The user's query.

    Returns:
        empl_and_wages_by_industry_df: A Pandas Dataframe containing the
            employment and wages by industry.
        unskilled_labor_salaries_df: A Pandas Dataframe containing the Unskilled labor
            salaries.
    """
    city_names = [f"{area.get('city_name')}" for area in metro_areas]
    found_titles, found_codes = extract_naics_info(user_query)
    print(found_titles)
    return "TEST"
    # Parallelize functions needed for metro matrix.
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = {
    #         # executor.submit(extract_naics_info, user_query): "naics_codes",
    #     }

    #     results = {}
    #     for future in concurrent.futures.as_completed(futures):
    #         key = futures[future]
    #         results[key] = future.result()

    # # Get results.
    # found_titles, found_codes = results["naics_codes"]
    # labor_force_stats, labor_force_citations = results["labor"]
    # state_tax, state_tax_citations = results["tax"]
    # median_hourly_wages, median_hourly_citations = results["wage"]
    # state_union_employment, union_citations = results["union"]

    # # Process citations for matrix.
    # metro_matrix_citations = join_sets(
    #     labor_force_citations,
    #     median_hourly_citations,
    #     search_citations,
    #     state_tax_citations,
    #     union_citations
    # )
    # citations = {"citations": metro_matrix_citations}

    # # Merge all data points.
    # merged_df = merge_dataframes(
    #     df_list=[
    #         forbes_ratings,
    #         labor_force_stats,
    #         median_hourly_wages,
    #         state_tax,
    #         state_union_employment
    #     ],
    #     how="left",
    #     on="city_name"
    # )

    # metro_matrix = format_metro_matrix_data(merged_df)
    # return metro_matrix, citations



def extract_naics_info(query):
    """
    Extracts NAICS codes and titles from a user query, handling misspellings and case sensitivity.

    Args:
        query (str): The user's query string.

    Returns:
        tuple: A tuple containing two lists - one with NAICS titles and the other with corresponding NAICS codes.
    """

    # Compile regex patterns (case-insensitive).
    code_pattern = re.compile(r'\b(\d{2,6})\b')
    # Extract all unique NAICS titles from the dataframe.
    titles = NAICS_MAPPING['2022 NAICS US Title'].unique()

    # Find all potential codes in the query
    code_matches = code_pattern.findall(query)
    title_matches = []
    # Calculate Levenshtein distance for each title.
    for title in titles:
        distance = Levenshtein.distance(query.lower(), title.lower())
        if distance <= 2:
            title_matches.append(title)

    found_titles = []
    found_codes = []
    found_pairs = set()  # Use a set to track (title, code) pairs.

    # Process code matches.
    for code in code_matches:
        # Find the row with the code.
        row = NAICS_MAPPING[NAICS_MAPPING['code'] == code]
        # If the code is found, add the title and code to the lists.
        if not row.empty:
            title = row.iloc[0]['2022 NAICS US Title']
            pair = (title, code)
            if pair not in found_pairs:
                found_titles.append(title)
                found_codes.append(code)
                found_pairs.add(pair)

    # Process title matches.
    for title in title_matches:
        # Find all rows with the title.
        rows = NAICS_MAPPING[NAICS_MAPPING['2022 NAICS US Title'] == title]
        # If the title is found, find the longest code and add the title and code to the lists.
        if not rows.empty:
            longest_code = max(rows['code'], key=len)
            pair = (title, longest_code)
            if pair not in found_pairs:
                found_titles.append(title)
                found_codes.append(longest_code)
                found_pairs.add(pair)

    return found_titles, found_codes
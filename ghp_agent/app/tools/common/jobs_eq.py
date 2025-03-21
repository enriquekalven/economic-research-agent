#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""JobsEQ Functions for tools."""


import concurrent.futures
import json
import Levenshtein
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types as genai_types
from google.cloud import bigquery
from langchain_core.tools import tool
import pandas as pd
import pydantic

from app.tools.common.gemini_sdk import GeminiSDKManager
from app.utils.helper import (
    execute_bq_query_to_df,
    merge_dataframes
)

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)  # Change the working directory
filepath = os.path.join(current_dir, "naics_mappings.csv")
NAICS_MAPPING = pd.read_csv(filepath)


def process_naics_requests(
    naics_requests: List[str],
    naics_dataframe: pd.DataFrame=NAICS_MAPPING,
):
    """
    Processes a list of strings containing NAICS codes and industry names, 
    checking against a Pandas DataFrame and returning unique industry names and NAICS codes.

    Args:
        naics_requests: A list of strings, where each string is either an 
                        industry name or a NAICS code.
        naics_dataframe: A Pandas DataFrame containing NAICS data, with columns
                         "NAICS Code" and "Industry Title".

    Returns:
        A tuple containing two lists:
            - A list of unique industry names.
            - A list of unique NAICS codes.
    """

    industry_names = set()
    naics_codes = set()

    # Create a dictionary for efficient lookup
    naics_data = {}
    for index, row in naics_dataframe.iterrows():
        code = str(row["code"]).strip() # convert to string to handle various datatypes.
        name = str(row["2022 NAICS US Title"]).strip().lower()
        naics_data[code] = name

    for item in naics_requests:
        item_lower = item.lower()
        if item.isdigit():
            if item in naics_data:
                naics_codes.add(item)
                industry_names.add(naics_data[item])
        else:
            if item_lower in naics_data.values():
                for code, name in naics_data.items():
                    if name == item_lower:
                        industry_names.add(name)
                        naics_codes.add(code)

    return list(industry_names), list(naics_codes)


def empl_and_wages_by_industry(
    city_names: List[str],
    naics_codes: List[str],
):
    """
    Query BigQuery/JobsEQ data for the industry employment and wages by industry table for Company Relocation.

    Args:
        city_names: List of city's requested by user.
        naics_codes: List of NAICS Codes requested for Industries.

    Returns:
        Pandas dataframe representing the industry employment and wages by industry table.
    """

    # Get subsector numbers.
    naics_where_clause = f"(Substring(code, 1, {len(naics_codes[0])}) = '{naics_codes[0]}'"
    # Find the longest NAICS code to find the number substring.
    max_length = len(naics_codes[0])
    for code in naics_codes[1:]:
        naics_where_clause = naics_where_clause + f" OR SUBSTR(code, 1, {len(code)}) = '{code}'"
        max_length = max(max_length, len(code))
    naics_where_clause = naics_where_clause + f") AND LENGTH(code) = {max_length+1}"
    naics_sql = f"SELECT code, `2022 NAICS US Title` FROM {NAICS_US_CODE_2022} WHERE {naics_where_clause};"

    # Get child NAICS sector names and codes for Each parent sector.
    naics_dig = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=naics_sql
    )

    # For each child sector, calculate Employment and Current Avg Ann Wages for that city
    city_where_clause = f"(LOWER(metro) LIKE LOWER('%{city_names[0]}%')"
    if len(city_names)>1:
        for city in city_names[1:]:
            city_where_clause = city_where_clause + f" OR LOWER(metro) LIKE LOWER('%{city}%')"
    city_where_clause = city_where_clause + ")"

    sub_sector_sql = f"""
    SELECT
      SUBSTR(code, 1, {max_length+1}) AS code,
      SUM(empl) AS sum_total_empl_int,
      SUM(avg_ann_wages_int)/SUM(empl) AS avg_avg_ann_wages_int,
      metro
    FROM
      {INDUSTRY_2024Q3} t
    WHERE
      {city_where_clause}
      AND
      SUBSTR(code, 1, {max_length+1}) IN {tuple(naics_dig["code"])} Group by metro, code;"""

    sub_sector_data = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=sub_sector_sql
    )

    # Combine with naics 3 dig table
    merged_df = merge_dataframes(
        df_list=[naics_dig, sub_sector_data],
        how="left",
        on="code"
    )
    # merged_df = pd.merge(naics_dig, sub_sector_data, left_on='code', right_on='code', how='left')

    sector_employment_and_wages_by_sub_sector = merged_df[["2022 NAICS US Title", "sum_total_empl_int", "avg_avg_ann_wages_int", "metro"]]
    sector_employment_and_wages_by_sub_sector = sector_employment_and_wages_by_sub_sector.rename(columns = {
        "2022 NAICS US Title": "Industry",
        "sum_total_empl_int": "Employment",
        "avg_avg_ann_wages_int": "Current Avg Ann Wages",
        "metro": "Metro"
    })# formatted with same names as template.

    return sector_employment_and_wages_by_sub_sector


def unskilled_labor_wages(
    city_names: List[str],
    naics_codes: List[str],
    naics_titles: List[str],
):
    """
    Query BigQuery/JobsEQ data for the unskilled labor salaries by job title table for Company Relocation.

    Args:
        city_names: List of cities requested by user.
        naics_codes: List of NAICS Codes requested for Industries.
        naics_titles: List of NAICS Titles requested for Industries.

    Returns:
        Pandas dataframe representing the unskilled labor salaries by job title table.
    """

    # Create the metro where clause.
    city_where_clause = f"(LOWER(metro) LIKE LOWER('%{city_names[0]}%')"
    if len(city_names)>1:
        for city in city_names[1:]:
            city_where_clause = city_where_clause + f" OR LOWER(metro) LIKE LOWER('%{city}%')"
    city_where_clause = city_where_clause + ")"
    industry_sql_query = f"SELECT soc, occupation FROM {OCCUPATION_WAGES_2024Q3} WHERE {city_where_clause};"

    # Get Instustry Occupation Data
    industry_occupations = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=industry_sql_query
    )

    # Send to Gemini to decide which to include
    model = GeminiSDKManager()
    occupation_selection_prompt = f""""For the industry sectors {naics_titles}, identify the most relevant occupations and their corresponding Standard Occupational Classification (SOC) codes from the following list.

    List of Occupations and SOC Codes:
    {industry_occupations}

    Instructions:
    1.  Focus specifically on each of the following industries:{naics_titles}.
    2.  Select only the occupations and SOC codes that are directly and significantly applicable to UNSKILL LABOR for the specified industries.
    3.  Exclude occupations that are clearly unrelated or have minimal relevance to all of the requested industries.
    4.  Exclude occupations that would be categoriezed as "skilled" labor, and only returned occupations that would be categorized as "unskilled".
    5.  The number of selected occupations should be around 15.
    6.  Prioritize occupations that are essential for the core functions of the requested industries.
    7.  Output the results as valid JSON, where the key is the SOC Code and the value is the Occupation title (e.g., {{"1234":"Operator"}}.
    8.  Do not output any explanation. Only output the JSON.

    Example Output:
    {{"11-1011": "occupation 1", "11-1021": "occupation 2", ... }}

    """
    response = model.send_request(
        contents=occupation_selection_prompt,
        response_mime_type = "application/json",
        )

    # Turn into dict.
    try:
        occupations = json.loads(response.candidates[0].content.parts[0].text)
        if len(occupations) == 0:
            return("Could not find Occupations given the requested Industries.")
    except json.JSONDecodeError:
        return("Could not find Occupations given the requested Industries.")

    # Use the selected occupations to create unskilled labor salaries by job title table.
    soc_codes = list(occupations.keys())
    soc_where_clause = f"(soc = '{soc_codes[0]}'"
    for soc in soc_codes[1:]:
        soc_where_clause = soc_where_clause + f" OR soc = '{soc}'"
    soc_where_clause = soc_where_clause + ")"
    unskilled_labor_query = f"SELECT occupation, mean, entry_level, experienced, metro FROM {OCCUPATION_WAGES_2024Q3} WHERE {soc_where_clause} AND {city_where_clause};"

    # Get Instustry Occupation Data
    unskilled_labor = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=unskilled_labor_query
    )

    return unskilled_labor

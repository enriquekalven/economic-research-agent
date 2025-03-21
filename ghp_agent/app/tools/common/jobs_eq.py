#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""JobsEQ Functions for tools."""


import json
import os
from typing import List

import pandas as pd

from app.tools.common.gemini_sdk import GeminiSDKManager
from app.utils.helper import (
    execute_bq_query_to_df,
    merge_dataframes
)
from app.utils.prompts import Prompts


PROJECT_ID = "ghp-poc"
REGION = "us-central1"
DATA_AXLE = "ghp-poc.jobseq.data_axle"
INDUSTRY_2024Q3 = "ghp-poc.jobseq.industry_2024q3_cleaned"
INDUSTRY_OCCUPATION_2024Q3 = "ghp-poc.jobseq.industry_occupation_mix_2024q3"
OCCUPATION_WAGES_2024Q3 = "ghp-poc.jobseq.`jobseq-occupation-wages-2024q3`"
NAICS_US_CODE_2022 = "ghp-poc.jobseq.naics_us_code_2022"

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)  # Change the working directory
filepath = os.path.join(current_dir, "naics_mappings.csv")
NAICS_MAPPING = pd.read_csv(filepath)


def get_process_naics_requests(
    naics_requests: List[str],
    naics_dataframe: pd.DataFrame=NAICS_MAPPING,
):
    """
    Processes a list of strings containing NAICS codes and industry names, 
    checking against a Pandas DataFrame and returning unique industry names
    and NAICS codes.

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
    for _, row in naics_dataframe.iterrows():
        code = str(row["code"]).strip()
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


def get_empl_and_wages_by_industry(
    city_names: List[str],
    naics_codes: List[str],
):
    """
    Query BigQuery/JobsEQ data for the industry employment and wages by
    industry table for Company Relocation.

    Args:
        city_names: List of city's requested by user.
        naics_codes: List of NAICS Codes requested for Industries.

    Returns:
        Pandas df representing the industry employment and wages table.
    """

    # Get subsector numbers.
    naics_where_clause = f"""(Substring(code, 1, {len(naics_codes[0])}) =
        '{naics_codes[0]}'"""
    # Find the longest NAICS code to find the number substring.
    max_length = len(naics_codes[0])
    for code in naics_codes[1:]:
        naics_where_clause = naics_where_clause + f""" OR
            SUBSTR(code, 1, {len(code)}) = '{code}'"""
        max_length = max(max_length, len(code))
        if not max_length == 6:
            max_length+=1
    naics_where_clause = naics_where_clause + f""") AND
        LENGTH(code) = {max_length}"""
    naics_sql = f"""SELECT code, `2022 NAICS US Title` FROM
        {NAICS_US_CODE_2022} WHERE {naics_where_clause};"""

    # Get child NAICS sector names and codes for Each parent sector.
    naics_dig = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=naics_sql
    )
    if naics_dig.empty:
        return "No Sub-Sectors found within the requested Industry."

    # For each child sector and city, get Employment and Current Avg Ann Wages.
    city_where_clause = f"(LOWER(metro) LIKE LOWER('%{city_names[0]}%')"
    if len(city_names)>1:
        for city in city_names[1:]:
            city_where_clause = city_where_clause + f""" OR
                LOWER(metro) LIKE LOWER('%{city}%')"""
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
        SUBSTR(code, 1, {max_length+1}) IN {tuple(naics_dig["code"])}
    GROUP BY metro, code;"""
    print(sub_sector_sql)

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

    empl_wages_table = merged_df[[
        "2022 NAICS US Title",
        "sum_total_empl_int",
        "avg_avg_ann_wages_int", "metro"
    ]]
    empl_wages_table = empl_wages_table.rename(columns = {
        "2022 NAICS US Title": "Industry",
        "sum_total_empl_int": "Employment",
        "avg_avg_ann_wages_int": "Current Avg Ann Wages",
        "metro": "Metro"
    })# formatted with same names as template.

    return empl_wages_table


def get_unskilled_labor_wages(
    city_names: List[str],
    naics_titles: List[str],
):
    """
    Query BigQuery/JobsEQ data for the unskilled labor salaries by
    job title table for Company Relocation.

    Args:
        city_names: List of cities requested by user.
        naics_titles: List of NAICS Titles requested for Industries.

    Returns:
        Pandas df representing the unskilled labor salaries by job title table.
    """

    # Create the metro where clause.
    city_where_clause = f"(LOWER(metro) LIKE LOWER('%{city_names[0]}%')"
    if len(city_names)>1:
        for city in city_names[1:]:
            city_where_clause = city_where_clause + f""" OR LOWER(metro)
                LIKE LOWER('%{city}%')"""
    city_where_clause = city_where_clause + ")"
    industry_sql_query = f"""SELECT soc, occupation FROM
        {OCCUPATION_WAGES_2024Q3} WHERE {city_where_clause};"""

    # Get Instustry Occupation Data
    industry_occupations = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=industry_sql_query
    )

    # Send to Gemini to decide which to include
    model = GeminiSDKManager()
    prompts = Prompts()
    occupation_selection_prompt = prompts.occupation_selection_prompt(
        naics_titles=naics_titles,
        industry_occupations=industry_occupations)
    response = model.send_request(
        contents=occupation_selection_prompt,
        response_mime_type = "application/json",
        )

    # Turn into dict.
    try:
        occupations = json.loads(response.candidates[0].content.parts[0].text)
        if len(occupations) == 0:
            return "Could not find Occupations given the requested Industries."
    except json.JSONDecodeError:
        return "Could not find Occupations given the requested Industries."
    print(occupations)
    # Use selected occupations to create unskilled labor salaries table.
    if isinstance(occupations, list): # Handle various LLM output.
        occupations = occupations[0]
    soc_codes = list(occupations.keys())
    soc_where_clause = f"(soc = '{soc_codes[0]}'"
    for soc in soc_codes[1:]:
        soc_where_clause = soc_where_clause + f" OR soc = '{soc}'"
    soc_where_clause = soc_where_clause + ")"
    unskilled_labor_query = f"""SELECT occupation, mean, entry_level,
        experienced, metro FROM {OCCUPATION_WAGES_2024Q3} WHERE
        {soc_where_clause} AND {city_where_clause};"""
    # Get Instustry Occupation Data
    unskilled_labor = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=unskilled_labor_query
    )

    return unskilled_labor

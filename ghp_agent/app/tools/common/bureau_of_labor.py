#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Bureau of Labor statistics functions for tools."""

from typing import Any, Dict, List

import pandas as pd

from app.utils.helper import execute_bq_query_to_df


PROJECT_ID = "ghp-poc"
LABOR_STATS_DATASET = "bls"


def get_labor_force_stats(
    city_names: List[str]
):
    """Get labor force stats from a city."""
    labor_force_table = "labor_force"

    city_name_lower_case = [city_name.lower() for city_name in city_names]
    city_names_regex = "|".join(city_name_lower_case)

    column_name_to_match = "area_name"

    labor_query = f"""
    SELECT
        area_name,
        labor_force,
        unemployment_rate,
        date,
        source
    FROM `{PROJECT_ID}.{LABOR_STATS_DATASET}.{labor_force_table}`
    WHERE REGEXP_CONTAINS(
        LOWER({column_name_to_match}),
        '{city_names_regex}'
    );
    """

    labor_force_stats = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=labor_query
    )

    def find_city(area_name):
        area_name_lower = area_name.lower()
        for city in city_name_lower_case:
            if city in area_name_lower:
                return city.capitalize()
        return None

    labor_force_stats["city_name"] = labor_force_stats["area_name"].apply(
        find_city)

    # Citations.
    citations = set(labor_force_stats["source"].unique())

    # Drop citation column.
    labor_force_stats.drop(
        ["source", "area_name"],
        inplace=True,
        axis=1
    )
    return labor_force_stats, citations


def get_state_tax_rates(
    metros: List[Dict[str,Any]]
):
    """Get State Tax Rates"""
    state_tax_table = "state_tax_rates"

    states = [metro.get("state", "") for metro in metros]

    column_name_to_match = "state"

    state_tax_query = f"""
    SELECT
        *
    FROM `{PROJECT_ID}.{LABOR_STATS_DATASET}.{state_tax_table}`
    WHERE {column_name_to_match} IN UNNEST({states})
    """

    state_tax_bq_results = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=state_tax_query
    )

    metro_df = pd.DataFrame(metros)

    state_tax_df = pd.merge(
        left=state_tax_bq_results,
        right=metro_df,
        on="state",
        how="left"
    )

    # Citations.
    citations = set(state_tax_bq_results["source"].unique())

    state_tax_df.drop(
        labels=["source", "state_abbreviation", "state"],
        axis=1,
        inplace=True
    )

    return state_tax_df, citations

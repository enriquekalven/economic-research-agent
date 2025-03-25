#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Tools to support Bureau of Labor statistics."""

from typing import List, Tuple

from langchain_core.tools import tool
import pandas as pd

from app.tools.common.bureau_of_labor import (
    get_labor_force_stats,
    get_median_hourly_wage,
    get_state_tax_rates,
    get_union_employment
)


@tool
def find_labor_force_stats(
    city_names: List[str],
) -> Tuple[pd.DataFrame, set]:
    """Use this tool whenever a user is looking for information on
    the labor force for a city or cities. This might include
    unemployment or labor force.

    Args:
        city_names (List[str]): A list of atleast 1 city that a user
            is looking for to get labor force statistics on.

    Returns:
        labor_force_df: A Pandas Dataframe containing the labor
            stats.
    """
    # Get Labor Force & Unemployement stats.
    labor_force_df, labor_force_citations = get_labor_force_stats(
        city_names=city_names)

    return labor_force_df, {"citations": labor_force_citations}


@tool
def find_median_hourly_wages(
    city_names: List[str],
) -> Tuple[pd.DataFrame, set]:
    """Use this tool whenever a user is looking for hourly median
    wages for a city or cities.

    Args:
        city_names (List[str]): A list of atleast 1 city that a user
            is looking for to get the median hourly wage for.

    Returns:
        median_hourly_wages: A Pandas Dataframe containing the hourly
            wages per hour.
    """
    median_hourly_wages, median_hourly_citations = get_median_hourly_wage(
        city_names=city_names)

    return median_hourly_wages, {"citations": median_hourly_citations}


@tool
def find_state_union_employment(
    state_names: List[str],
) -> Tuple[pd.DataFrame, set]:
    """Use this tool whenever a user is looking for union
    employment rates for a state.

    Args:
        state_anmes (List[str]): A list of atleast 1 state that a user
            is looking for to get the union employment rate for.

    Returns:
        union_employment_rate: A Pandas Dataframe containing the hourly
            state union employment rates.
    """
    metros = []
    for state in state_names:
        metros.append({
            "state": state
        })

    state_union_employment, union_citations = get_union_employment(
        metros=metros, drop_state=False)
    return state_union_employment, {"citations": union_citations}


@tool
def find_state_tax_rate(
    state_names: List[str],
) -> Tuple[pd.DataFrame, set]:
    """Use this tool whenever a user is looking for tax
    rates for a state.

    Args:
        state_anmes (List[str]): A list of atleast 1 state that a user
            is looking for to get the tax rate for a state.

    Returns:
        state_tax_rate_df: A Pandas Dataframe containing the hourly
            state union employment rates.
    """
    try:
        metros = []
        for state in state_names:
            metros.append({
                "state": state
            })

        state_tax_rate_df, state_tax_citations = get_state_tax_rates(
            metros=metros, drop_state=False)
    except Exception as e:
        return e

    return state_tax_rate_df, {"citations": state_tax_citations}

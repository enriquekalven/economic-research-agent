#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Tools to support Bureau of Labor statistics."""

from typing import List, Tuple

from langchain_core.tools import tool
import pandas as pd

from app.tools.common.bureau_of_labor import get_labor_force_stats


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

    return labor_force_df, labor_force_citations

#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting company relocation workflow."""

import json
import logging
from typing import Any, Dict, List, Tuple

from google.genai import types
from langchain_core.tools import tool
import pandas as pd

from app.tools.common.bureau_of_labor import (
    get_labor_force_stats,
    get_median_hourly_wage,
    get_state_tax_rates
)
from app.tools.common.gemini_sdk import GeminiSDKManager
from app.utils.helper import (
    join_sets,
    merge_dataframes
)



DATA_AXLE = "ghp-poc.jobseq.data_axle"
PROJECT_ID = "ghp-poc"
LABOR_STATS_DATASET = "bls"


# Logger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def find_metro_matrix(
    metro_areas: List[Dict[str, Any]],
) -> Tuple[pd.DataFrame, set]:
    """Search for overall metro data for each specified city.

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

    Returns:
        metro_matrix_df: A Pandas Dataframe containing the metro
            matrix.
    """
    city_names = [f"{area.get('city_name')}" for area in metro_areas]

    # Get Forbes best business rankings.
    forbes_ratings, search_citations = search_google_for_forbes(
        city_names=city_names)

    # Get Labor Force & Unemployement stats.
    labor_force_stats, labor_force_citations = get_labor_force_stats(
        city_names=city_names)

    # Get State Tax rates.
    state_tax, state_tax_citations = get_state_tax_rates(
        metros=metro_areas)


    # Get median hourly wages by cities.
    median_hourly_wages, median_hourly_citations = get_median_hourly_wage(
        city_names=city_names)


    # Process citations for matrix.
    metro_matrix_citations = join_sets(
        labor_force_citations,
        median_hourly_citations,
        search_citations,
        state_tax_citations
    )
    citations = {"citations": metro_matrix_citations}

    # Merge all data points.
    merged_df = merge_dataframes(
        df_list=[
            forbes_ratings,
            labor_force_stats,
            median_hourly_wages,
            state_tax
        ],
        how="left",
        on="city_name"
    )

    metro_matrix = format_metro_matrix_data(merged_df)

    return metro_matrix, citations


def format_metro_matrix_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """

    Args:
        Dataframe containing data from query.

    Returns:
        Dataframe to display to user for metro matrix.
    """
    df.set_index("city_name", inplace= True)
    return df.T



def search_google_for_forbes(
    city_names: List[str]
):
    """Uses search tool to get best rankings."""
    model = GeminiSDKManager()

    # Call search tool with city names.
    search_tool_prompt = f"""
    Find the `Forbes Best Places for Business & Careers` rankings for each of the cities provided here only
    using www.forbes.com

    You should only ever return one ranking for each city name and it should be the one for
    `Forbes Best Places for Buiness & Careers`.

    cities:
    {", ".join(city_names)}
    """
    # Google search tool.
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]

    grounded_search_response = model.send_request(
        contents=[search_tool_prompt],
        tools=tools
    )
    search_citations = model.get_url_citations(
        response=grounded_search_response)

    # Format raw search text response to a JSON.
    # Controlled generation schema.
    rankings_output_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "city_name": {"type": "STRING"},
                "ranking": {"type": "INTEGER"}

            },
            "required": ["city_name", "ranking"],
        },
    }
    format_output_schema_prompt = f"""
    Convert this input of text to a dictionary following this schema:
    {{
        "city_name": "[INTEGER OF RANKING]"
    }}

    input:
    {grounded_search_response.text}
    """
    formatted_output_response = json.loads(
        model.send_request(
            contents=format_output_schema_prompt,
            response_schema=rankings_output_schema,
            response_mime_type="application/json"
        ).text
    )

    # List to store results.
    cities_forbes_rankings = []

    # Loop through each formatted city with it's ranking.
    for city_res in formatted_output_response:
        location = city_res.get("city_name", None)
        city_name = location.split(", ")[0]
        ranking = city_res.get("ranking", None)
        if city_name is not None and ranking is not None:
            cities_forbes_rankings.append({
                "city_name": city_name,
                "forbes_ranking": ranking
            })

    cities_forbes_rankings_df = pd.DataFrame(
        columns=[
            "city_name",
            "forbes_ranking",
        ],
        data=cities_forbes_rankings
    )

    return cities_forbes_rankings_df, search_citations

#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Census API functions for tools."""

import requests
from typing import Any, Dict, List

from census import Census
import pandas as pd

from app.utils.helper import execute_bq_query_to_df


# TODO: upload to secret manager.
CENSUS_API_KEY = "04fe998bc89ff6fef628edd3281c2bc170448718"
c = Census(CENSUS_API_KEY)

PROJECT_ID = "ghp-poc"
CENSUS_DATASET = "census"


def get_state_fips(state_name):
    url = "https://api.census.gov/data/2021/pep/population?get=NAME,STATE&for=state:*" #pylint: disable=line-too-long
    response = requests.get(url, timeout=100)
    data = response.json()

    for row in data[1:]:  # Skip header row.
        if row[0].lower() == state_name.lower():
            return row[1]  # Return the state FIPS code.
    return None


def get_place_fips(city_name, state_fips):
    places = c.acs1.get(["NAME"],
                         {"for": "place:*", "in": f"state:{state_fips}"})

    for place in places:
        if city_name.lower() in place["NAME"].lower():
            return place["place"]
    return None


def get_one_city_statistics(
        city_name: str,
        state_name: str
    ):
    """Fetches various statistics for the given city_name and state_name
    from Census API.
    """
    print(f"Getting census for {city_name}")

    citations = "https://api.census.gov/data/2021/pep/population?get=NAME,STATE&for=state:*" #pylint: disable=line-too-long

    state_fips = get_state_fips(state_name)
    if not state_fips:
        return f"State '{state_name}' not found."

    place_fips = get_place_fips(city_name, state_fips)

    if not place_fips:
        return f"City '{city_name}' not found in {state_name}."

    variables = {
        "median_age": "B01002_001E",
        "foreign_born": "B05012_003E",
        "total_population": "B01003_001E",
        "bachelors_higher": [
            "B15003_022E",
            "B15003_023E",
            "B15003_024E",
            "B15003_025E"
        ],
        "graduate_degree": ["B15003_024E", "B15003_025E"],
        "total_25plus": "B15003_001E"
    }


    # Fetch data.
    result = c.acs1.get(
        [
            variables["median_age"],
          variables["foreign_born"],
          variables["total_population"],
          *variables["bachelors_higher"],
          *variables["graduate_degree"],
          variables["total_25plus"]],
        {"for": f"place:{place_fips}", "in": f"state:{state_fips}"},
    )

    if not result:
        return {}

    data = result[0]

    total_population = float(data.get(variables["total_population"], 0))
    total_25plus = float(data.get(variables["total_25plus"], 0))

    bachelors_higher_count = sum(
        float(data.get(var, 0))
        for var in variables["bachelors_higher"]
    )
    graduate_degree_count = sum(
        float(data.get(var, 0))
        for var in variables["graduate_degree"]
    )
    foreign_born_count = float(data.get(variables["foreign_born"], 0))

    stats = {
        "city_name": city_name,
        "Total Population": total_population,
        "Population above 25 age": total_25plus,
        "Median Age": float(data.get(variables["median_age"], 0)),
        "Percent Foreign Born":
        (foreign_born_count / total_population)\
              * 100 if total_population else 0,
        "Percent Earned Bachelor's Degree or Higher (25+)":
            (bachelors_higher_count / total_25plus)\
                  * 100 if total_25plus else 0,
        "Percent Earned Graduate or Professional Degree (25+)":
          (graduate_degree_count / total_25plus)\
              * 100 if total_25plus else 0
    }

    return stats, citations


def get_city_statistics(metros: List[Dict[str,Any]]):
    city_names = [metro.get("city_name", "") for metro in metros]
    states = [metro.get("state", "") for metro in metros]
    all_stats = []
    for city_name, state in zip(city_names, states):
        stats = get_one_city_statistics(city_name, state)
        all_stats.append(stats)
    return pd.DataFrame(all_stats)


def get_census_stats(city_names: List[Dict[str, Any]]):
    """Query BQ for censs stats."""
    census_table = "census_sample"

    city_name_lower_case = [city_name.lower() for city_name in city_names]
    city_names_regex = "|".join(city_name_lower_case)

    column_name_to_match = "city_name"

    census_query = f"""
    SELECT
        city_name,
        CONCAT(total_population, ' (2023)') as total_population,
        CONCAT(median_age, ' (2023)') as median_age,
        CONCAT(population_above_25, ' (2023)') as population_above_25,
        CONCAT(FORMAT('%#.2f', CAST(percent_bachelors AS FLOAT64)), '% (2023)') AS percent_bachelors,
        CONCAT(FORMAT('%#.2f',CAST(percent_masters AS FLOAT64)), '% (2023)') AS percent_masters,
        source
    FROM `{PROJECT_ID}.{CENSUS_DATASET}.{census_table}`
    WHERE REGEXP_CONTAINS(
        LOWER({column_name_to_match}),
        '{city_names_regex}'
    );
    """

    census_stats = execute_bq_query_to_df(
        project=PROJECT_ID,
        query=census_query
    )

    def capitalize_city_name(city_name):
        return city_name.capitalize()

    census_stats["city_name"] = census_stats["city_name"].apply(
        capitalize_city_name)

    # Citations.
    citations = set(census_stats["source"].unique())

    # Drop citation column.
    census_stats.drop(
        ["source"],
        inplace=True,
        axis=1
    )

    return census_stats, citations

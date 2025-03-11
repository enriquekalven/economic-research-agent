#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting head quarter relocation workflow."""

import pandas as pd
from server.agent.models import HQRelocation, HQRelocationResult
from google.cloud import bigquery
from typing import Optional

from server.agent.models import HQRelocation, HQRelocationResult

DATA_AXLE = "ghp-poc.jobseq.data_axle"
PROJECT_ID = "ghp-poc"


def find_hq_relocation(
    city_name: str,
    industry: Optional[str] = None,
    state_name: Optional[str] = None,
) -> HQRelocationResult:
    f"""Search for Company Headquarters Relocation Data.

    Args:
        city_name (str): The name of the city.
        state_name (str): The 2-letter abbreviation of the state specified by the user.
        industry (str): The industry of the comapny considering Head Quarter relocation.

    Returns:
        HQRelocationResult: The return value. Object including overall industry data for the city, state.
    """

    # Initialize query parameters
    query_parameters = list[
        bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter
    ]()

    # probably convert city and state into some kind of number ##
    city_selector = None
    if city_name:
        city_selector = f"req_city.City = '{city_name}'"
        query_parameters.extend(
            [
                bigquery.ScalarQueryParameter(
                    name="city_name",
                    type_=bigquery.SqlParameterScalarTypes.STRING,
                    value=city_name,
                ),
            ]
        )
        if state_name:
            city_selector = f"req_city.City = '{city_name}' AND req_city.State = '{state_name}'"
            query_parameters.extend(
                [
                    bigquery.ScalarQueryParameter(
                        name="state_name",
                        type_=bigquery.SqlParameterScalarTypes.STRING,
                        value=state_name,
                    ),
                ]
            )
    where_clause = ""
    if city_selector:
        where_clause = f"WHERE {city_selector}"

    select_city_query = f"SELECT * FROM {DATA_AXLE}"

    # TODO: UPDATE THIS - just test

    query = f"""
SELECT
    req_city.City,
    req_city.State,
    req_city.County,
    req_city.`Primary SIC Description` as Industry
FROM
    ({select_city_query}) AS req_city
{where_clause} LIMIT 1
""".strip()

    query_job_config = bigquery.QueryJobConfig()
    query_job_config.query_parameters = query_parameters

    bq_client = bigquery.Client(project=PROJECT_ID)
    query_job = bq_client.query(
        query=query,
        job_config=query_job_config,
    )

    query_df: pd.DataFrame = query_job.to_dataframe()

    city_analysis = [
        HQRelocation.model_validate(row.to_dict()) for idx, row in query_df.iterrows()
    ]

    return HQRelocationResult(city_analysis=city_analysis)
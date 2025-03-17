#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting company relocation workflow."""

import logging
from typing import Optional

from google.cloud import bigquery
from langchain_core.tools import tool
import pandas as pd

from app.utils.models import MetroMatrixResult


DATA_AXLE = "ghp-poc.jobseq.data_axle"
PROJECT_ID = "ghp-poc"

# Logger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def find_metro_matrix(
    city_name: str,
    state_name: Optional[str] = None,
) -> MetroMatrixResult:
    """Search for overall metro data for each specified city.

    Args:
        city_name (str): The name of the city.
        state_name (Optional, str): The 2-letter abbreviation
            of the state specified by the user.

    Returns:
        MetroMatrixResult: The return value. Object including
            overall data for the city, state.
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
            city_selector = f"""req_city.City = '{city_name}'
                AND req_city.State = '{state_name}'"""
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

    # TODO: UPDATE THIS - just test.

    query = f"""
    SELECT
        req_city.City as city,
        req_city.State as state,
        req_city.County as county
    FROM
        ({select_city_query}) AS req_city
    {where_clause} LIMIT 10
    """.strip()

    query_job_config = bigquery.QueryJobConfig()
    query_job_config.query_parameters = query_parameters

    bq_client = bigquery.Client(project=PROJECT_ID)
    query_job = bq_client.query(
        query=query,
        job_config=query_job_config,
    )

    query_df: pd.DataFrame = query_job.to_dataframe()
    return query_df

    # city_analysis = [
    #     MetroMatrix.model_validate(row.to_dict())
    #     for idx, row in query_df.iterrows()
    # ]

    # return MetroMatrixResult(city_analysis=city_analysis)

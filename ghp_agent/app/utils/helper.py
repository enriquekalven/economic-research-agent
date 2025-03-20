#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Utility Functions."""

from google.cloud import bigquery
import pandas as pd


def execute_bq_query_to_df(project: str, query: str) -> pd.DataFrame:
    """Executes a BigQuery query and returns query results.

    Args:
        project: The Google Cloud project ID.
        query: The BigQuery query string.

    Returns:
        A list of dictionaries, where each dictionary
            represents a row in the query results.
    """

    client = bigquery.Client(project=project)

    results = client.query_and_wait(query).to_dataframe()

    return results


def join_sets(*sets) -> set:
    """Join multiple sets and return set with unique elements.

    Args:
        *sets: Variable number of sets to join.
    """
    resulting_set = set()
    for s in sets:
        resulting_set.update(s)
    return resulting_set


def merge_dataframes(
    df_list,
    how='outer',
    on=None
):
    """
    Merges a list of DataFrames into a single DataFrame.

    Args:
        df_list (list): A list of pandas DataFrames to merge.

    Returns:
        pandas.DataFrame: The merged DataFrame,
            or None if the input list is empty.
    """
    try:
        if not df_list:
            return None

        merged_df = df_list[0]

        for df in df_list[1:]:
            merged_df = pd.merge(
                merged_df,
                df,
                how=how,
                on=on
            )

        return merged_df
    except Exception as e:
        raise e

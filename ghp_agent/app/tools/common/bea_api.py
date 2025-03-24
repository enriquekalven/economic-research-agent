#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Bureau of Economic Analysis functions for tools."""

import functools
import json
import logging
import os
import requests
from typing import List

from google.cloud import logging as google_cloud_logging
import pandas as pd

logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)


# TODO: replace to retrieve programatically by metro.
PLACE_FIPS = {
    "atlanta": "12060",
    "austin": "12420",
    "chicago": "16980",
    "dallas": "19100",
    "houston": "26420",
    "reno": "39900",
    "tulsa": "46140"
}


@functools.lru_cache
def get_bea_gdp(place_fips, year="2023", url="https://apps.bea.gov/api/data/"):
    """API request to BEA for GDP by metro."""
    params = {
        "UserID": os.environ["BEA_API_KEY"],
        "method": "GetData",
        "DataSetName": "Regional",
        "TableName": "CAGDP2",
        "LineCode": "1",
        "GeoFips": place_fips,
        "Year": year,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = json.loads(response.content)
        response_value = data["BEAAPI"]["Results"]["Data"]
    except Exception as e:
        logging.error("Failed to fetch GDP By Metropolitan: %s", str(e))

    return response_value


def get_metros_gdps(city_names: List[str]):
    """Get GDP by Metro."""
    # List to store GDPs by region.
    try:
        gdps = []

        gdp_year = "2023"

        for city in city_names:
            # Map metro name to a fips code.
            curr_metro_fips = PLACE_FIPS.get(city.lower(), None)
            if curr_metro_fips is not None:
                metro_gdp_resp = get_bea_gdp(
                    place_fips=curr_metro_fips, year=gdp_year)
                # Parse API response.
                metro_gdp = metro_gdp_resp[0]["DataValue"]

                # Format gdp for dataframe.
                metro_gdp_formatted = f"{int(metro_gdp):,}"
                gdp_with_year = f"{metro_gdp_formatted} ({gdp_year})"

                gdps.append({
                    "city_name": city,
                    "gdp": gdp_with_year,
                })

        # Convert GDP results to dataframe.
        gdp_df = pd.DataFrame(data=gdps)
        # GDP citation.
        gdp_citations = {"https://apps.bea.gov/itable/"}

        return gdp_df, gdp_citations
    except Exception as e:
        raise e

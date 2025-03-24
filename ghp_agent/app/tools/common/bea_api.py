#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Bureau of Economic Analysis functions for tools."""

import logging
import requests
import json
import os
import functools
from google.cloud import logging as google_cloud_logging

logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)


@functools.lru_cache
def get_bea_gdp(place_fips, year="2023", url="https://apps.bea.gov/api/data/"):

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


if __name__ == "__main__":
    print(get_bea_gdp("12086"))

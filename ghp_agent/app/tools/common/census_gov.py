from census import Census
from us import states
import requests
import json
import pandas as pd
from typing import Any, Dict, List
import functools


CENSUS_API_KEY = "04fe998bc89ff6fef628edd3281c2bc170448718"
c = Census(CENSUS_API_KEY)


def get_state_fips(state_name):
    url = "https://api.census.gov/data/2021/pep/population?get=NAME,STATE&for=state:*"
    response = requests.get(url)
    data = response.json()

    for row in data[1:]:  # Skip header row
        if row[0].lower() == state_name.lower():
            return row[1]  # Return the state FIPS code
    return None

def get_place_fips(city_name, state_fips):
    places = c.acs1.get(["NAME"], {'for': 'place:*', 'in': f'state:{state_fips}'})

    for place in places:
        if city_name.lower() in place["NAME"].lower():
            return place["place"]
    return None


@functools.lru_cache
def get_city_statistics(metros: List[Dict[str,Any]]):
    city_names = [metro.get("city_name", "") for metro in metros]
    states = [metro.get("state", "") for metro in metros]
    all_stats = []
    for city_name, state in zip(city_names, states):
        stats = get_one_city_statistics(city_name, state)
        all_stats.append(stats)
    return pd.DataFrame(all_stats)

def get_one_city_statistics(city_name: str, state_name: str):
    """Fetches various statistics for the given city_name and state_name from Census API
Median Age: "B01002_001E"
Total population 25+ yrs: "B15003_001E"
Percent Foreign Born: "B05012_003E" (Foreign-born population) / "B01003_001E" (Total population)
Percent Earned Bachelor's Degree or Higher (25 yrs and over), 2023: "B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E" (Sum of these categories) / "B15003_001E"
Percent Earned Graduate or Professional Degree (25 yrs and over), 2023: "B15003_024E" (Master's), "B15003_025E" (Doctorate/Professional) / "B15003_001E"
"""

    # citations = "https://api.census.gov/data/2021/pep/population?get=NAME,STATE&for=state:*"
    # return {'city_name': 'San Francisco', 'Total Population': 808437.0, 'Population above 25 age': 644349.0, 'Median Age': 40.4, 'Percent Foreign Born': 33.174755732357625, "Percent Earned Bachelor's Degree or Higher (25+)": 61.39359260276651, 'Percent Earned Graduate or Professional Degree (25+)': 9.231177514049064}, citations

    print(f"Fetching data for {city_name}, {state_name}")

    state_fips = get_state_fips(state_name)
    if not state_fips:
        print(f"State '{state_name}' not found.")
        return
    print(state_fips)
    place_fips = get_place_fips(city_name, state_fips)
    if not place_fips:
        print(f"City '{city_name}' not found in {state_name}.")
        return
    print(place_fips)
    variables = {
        "median_age": "B01002_001E",
        "foreign_born": "B05012_003E",
        "total_population": "B01003_001E",
        "bachelors_higher": ["B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E"],
        "graduate_degree": ["B15003_024E", "B15003_025E"],
        "total_25plus": "B15003_001E"
    }


    # Fetch data
    result = c.acs1.get(
        [variables["median_age"], variables["foreign_born"], variables["total_population"],
         *variables["bachelors_higher"], *variables["graduate_degree"], variables["total_25plus"]],
        {'for': f'place:{place_fips}', 'in': f'state:{state_fips}'}
    )

    if not result:
        print("No data found.")
        return {}

    data = result[0]

    total_population = float(data.get(variables["total_population"], 0))
    total_25plus = float(data.get(variables["total_25plus"], 0))

    bachelors_higher_count = sum(float(data.get(var, 0)) for var in variables["bachelors_higher"])
    graduate_degree_count = sum(float(data.get(var, 0)) for var in variables["graduate_degree"])
    foreign_born_count = float(data.get(variables["foreign_born"], 0))

    # print(data)
    stats = {
        "city_name": city_name,
        "Total Population": total_population,
        "Population above 25 age": total_25plus,
        "Median Age": float(data.get(variables["median_age"], 0)),
        "Percent Foreign Born": (foreign_born_count / total_population) * 100 if total_population else 0,
        "Percent Earned Bachelor's Degree or Higher (25+)": (bachelors_higher_count / total_25plus) * 100 if total_25plus else 0,
        "Percent Earned Graduate or Professional Degree (25+)": (graduate_degree_count / total_25plus) * 100 if total_25plus else 0
    }

    return stats


# print(pd.DataFrame([get_city_statistics("San Francisco", "California")]))
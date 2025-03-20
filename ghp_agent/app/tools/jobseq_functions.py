#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Tools to support JobsEQ statistics."""

import pandas as pd
import re
import Levenshtein

from app.tools.common.jobs_eq import (
    extract_naics_info
)

# Mapping of NAICS codes and industry titles.
csv_file_path = "common/naics_mappings.csv"
naics_mappings = pd.read_csv(csv_file_path)


# @tool
# def extract_naics_info(
#     query:str
# ) -> Tuple[List[str], set]:
#     """
#     Extracts NAICS codes and titles from a user query, handling misspellings and case sensitivity.
#     This is needed to query 

#     Args:
#         query (str): The user's query string.

#     Returns:
#         tuple: A tuple containing two lists - one with NAICS titles and the other with corresponding NAICS codes.
#     """

#     # Compile regex patterns (case-insensitive).
#     code_pattern = re.compile(r'\b(\d{2,6})\b')
#     # Extract all unique NAICS titles from the dataframe.
#     titles = dnaics_mappingsf['2022 NAICS US Title'].unique()

#     # Find all potential codes in the query
#     code_matches = code_pattern.findall(query)
#     title_matches = []
#     # Calculate Levenshtein distance for each title.
#     for title in titles:
#         distance = Levenshtein.distance(query.lower(), title.lower())
#         if distance <= 2:
#             title_matches.append(title)

#     found_titles = []
#     found_codes = []
#     found_pairs = set()  # Use a set to track (title, code) pairs.

#     # Process code matches.
#     for code in code_matches:
#         # Find the row with the code.
#         row = naics_mappings[naics_mappings['code'] == code]
#         # If the code is found, add the title and code to the lists.
#         if not row.empty:
#             title = row.iloc[0]['2022 NAICS US Title']
#             pair = (title, code)
#             if pair not in found_pairs:
#                 found_titles.append(title)
#                 found_codes.append(code)
#                 found_pairs.add(pair)

#     # Process title matches.
#     for title in title_matches:
#         # Find all rows with the title.
#         rows = naics_mappings[naics_mappings['2022 NAICS US Title'] == title]
#         # If the title is found, find the longest code and add the title and code to the lists.
#         if not rows.empty:
#             longest_code = max(rows['code'], key=len)
#             pair = (title, longest_code)
#             if pair not in found_pairs:
#                 found_titles.append(title)
#                 found_codes.append(longest_code)
#                 found_pairs.add(pair)

#     return found_titles, found_codes

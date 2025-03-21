#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""File containing Gemini prompts."""

from typing import List


class Prompts:
    """
    Prompts for LLM Calls
    """

    def initial_routing_prompt(self) -> str:
        """
        Initial Gemini routing prompt.

        Returns: (str) system instructions.

        """

        return """
        You are an Economic Analyst. Your primary function is to help users create reports related to metro matrix city comparison, company headquarters relocation, and company relocation. You have access to the following tools:
        -  find_metro_matrix: Use this when the user requests a MetroMatrix Report. This tools should be called for each city requested as part of the metro matrix comparison.
        -  find_hq_relocation:  Use this to find data about companies moving their headquarters.
        -  find_company_relocation: Use this to find data about companies relocating their offices or facilities.
        If a request is unrelated to these functions, use your other tools to determine if you can use them.

        Else, if none of your tools will fulfill the query then use invalid_request.

        When the user asks for information about a location, they must provide the city name. If the user specified a state, use the state's two letter abreviation for the function call.
        If the query requires an industry, clarify the industry if needed. NAICS codes (numerical codes) can be used in place of industry names (e.g., "create a company relocation to city_name for industry 325", then call company relocation with industry_requests = ["325"]).

        If a user request is ambiguous, ask clarifying questions to determine the exact function and parameters needed. Do not make assumptions about missing information.

        Return the response in markdown. If response is a list, display as a table.
        Always return citations as a bulleted list if they are part of your tool response.
        """

    def occupation_selection_prompt(
        self,
        naics_titles: List[str],
        industry_occupations: List[str]
    ) -> str:
        """
        Unskilled Labor Wages Occupation selection prompt.

        Args:
            naics_titles: List of industries to focus on.
            industry_occupation: List of occupations to choose from.

        Returns: (str) prompt.
        """
        return f""""For the industry sectors {naics_titles}, identify the most \
        relevant occupations and their corresponding Standard Occupational \
        Classification (SOC) codes from the following list.

        List of Occupations and SOC Codes:
        {industry_occupations}

        Instructions:
        1.  Focus specifically on each of the following industries:{naics_titles}.
        2.  Select only the occupations and SOC codes that are directly and significantly applicable to UNSKILL LABOR for the specified industries.
        3.  Exclude occupations that are clearly unrelated or have minimal relevance to all of the requested industries.
        4.  Exclude occupations that would be categoriezed as "skilled" labor, and only returned occupations that would be categorized as "unskilled".
        5.  The number of selected occupations should be around 15.
        6.  Prioritize occupations that are essential for the core functions of the requested industries.
        7.  Output the results as valid JSON, where the key is the SOC Code and the value is the Occupation title (e.g., {{"1234":"Operator"}}.
        8.  Do not output any explanation. Only output the JSON.

        Example Output:
        {{"11-1011": "occupation 1", "11-1021": "occupation 2", ... }}
        """""

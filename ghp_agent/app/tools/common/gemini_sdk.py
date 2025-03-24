#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions supporting Gemini SDK - not integrated into langchain."""

import os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types


PROJECT_ID = "ghp-poc"
LOCATION = "us-central1"


class GeminiSDKManager:
    """SDK manager for Google Gemini."""
    def __init__(
        self,
        project_id: str = PROJECT_ID,
        location: str = LOCATION,
        vertexai: bool = True,
    ):
        self.client = self.load_client(
            project_id=project_id,
            location=location,
            vertexai=vertexai
        )

    def load_client(
        self,
        project_id: str,
        location: str,
        vertexai: str
    ) -> genai.Client:
        """Utilize Google GenAI SDK."""
        return genai.Client(
            project=project_id,
            location=location,
            vertexai=vertexai,
        )

    def send_request( # pylint: disable=too-many-positional-arguments
        self,
        contents: List[types.Content],
        response_mime_type: str = None,
        tools: Optional[List[types.Tool]] = None,
        model_name: str = "gemini-2.0-flash-001",
        response_schema: Optional[Dict[str, Any]] = None
    ) -> types.GenerateContentResponse:
        """Send request to Gemini client.

        Args:
            contents (List[Content]): Prompts to send to Gemini.
            response_mime_type (str): Config to generate text or JSON.
            tools: List of Gemini SDK tools.
            model_name: Gemini model name & version.
            response_schema: Dictionary to conform response to.
        """
        if response_mime_type is not None:
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type=response_mime_type,
                    response_schema=response_schema
                )
            )
        elif tools is not None:
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=tools
                )
            )
        else:
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents
            )
        return response

    def get_url_citations(
        self,
        response: types.GenerateContentResponse
    ) -> set:
        """Return citations from grounded search."""
        citations = set()
        grounding_metadata = response.candidates[0].grounding_metadata
        for grounded_metadata in grounding_metadata.grounding_chunks:
            webpage_title = grounded_metadata.web.title
            citations.add(
                f"https://{webpage_title}"
                if "https://" not in webpage_title
                else webpage_title
            )
        return citations



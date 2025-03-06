#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Pydantic models for chat agent."""

from pydantic import BaseModel


class MessageRequest(BaseModel):
    """Model for a request to chat agent."""
    session_id: str
    text: str

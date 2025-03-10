#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""File with Pydantic models."""

import pydantic
from typing import Optional

# Data Models
class MetroMatrix(pydantic.BaseModel):
    """
    Metro Matrix workflow object.
    """
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None

class HQRelocation(pydantic.BaseModel):
    """
    Head Quarter Relocation workflow object.
    """
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    industry: Optional[str] = None

class CompanyRelocation(pydantic.BaseModel):
    """
    Company Relocation workflow object.
    """
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    industry: Optional[str] = None

# Tool Return Types
class MetroMatrixResult(pydantic.BaseModel):
    """
    Metro Matrix analysis result object.
    """
    city_analysis: list[MetroMatrix] = []
    error: Optional[str] = None

class HQRelocationResult(pydantic.BaseModel):
    """
    Head Quarter Relocation analysis result object.
    """
    city_analysis: list[HQRelocation] = []
    error: Optional[str] = None

class CompanyRelocationResult(pydantic.BaseModel):
    """
    Company Relocation Result analysist result object.
    """
    city_analysis: list[CompanyRelocation] = []
    error: Optional[str] = None

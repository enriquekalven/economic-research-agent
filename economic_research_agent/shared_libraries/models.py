#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""Pydantic models for Economic Research Agent (ERA)."""

from typing import Optional, List
from pydantic import BaseModel


class MetroMatrix(BaseModel):
    """Metro Matrix workflow object."""
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None


class HQRelocation(BaseModel):
    """Head Quarter Relocation workflow object."""
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    industry: Optional[str] = None


class CompanyRelocation(BaseModel):
    """Company Relocation workflow object."""
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    industry: Optional[str] = None


class MetroMatrixResult(BaseModel):
    """Metro Matrix analysis result object."""
    city_analysis: List[MetroMatrix] = []
    error: Optional[str] = None


class HQRelocationResult(BaseModel):
    """Head Quarter Relocation analysis result object."""
    city_analysis: List[HQRelocation] = []
    error: Optional[str] = None


class CompanyRelocationResult(BaseModel):
    """Company Relocation Result analysist result object."""
    city_analysis: List[CompanyRelocation] = []
    error: Optional[str] = None

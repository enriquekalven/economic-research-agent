# Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""Unit tests for the Economic Research Agent (ERA) skills suite."""

import json
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Skill Imports
from economic_research_agent.tools.fred_skill import fetch_regional_macro_stats
from economic_research_agent.tools.eia_skill import fetch_state_electricity_rates
from economic_research_agent.tools.real_estate_skill import get_real_estate_roi
from economic_research_agent.tools.sentiment_skill import analyze_market_sentiment
from economic_research_agent.tools.climate_resilience_skill import get_climate_risk_index
from economic_research_agent.tools.lifestyle_logistics_incentives_skills import (
    get_logistics_efficiency,
    get_cultural_amenity_score,
    get_regional_tax_incentives
)
from economic_research_agent.tools.policy_risk_cola_skills import (
    get_policy_risk_benchmarks,
    get_purchasing_power_adjustment
)

@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for all tests."""
    with patch.dict(os.environ, {
        "FRED_API_KEY": "mock_fred_key",
        "EIA_API_KEY": "mock_eia_key",
        "NEWS_API_KEY": "mock_news_key",
        "HUD_API_KEY": "mock_hud_key",
        "BLS_API_KEY": "mock_bls_key"
    }, clear=False):
        yield

def test_fred_skill_success(mock_env):
    """Test successful retrieval of FRED macro stats."""
    with patch('economic_research_agent.tools.fred_skill.Fred') as MockFred:
        mock_instance = MockFred.return_value
        
        # Create a real pandas series mock
        dates = pd.date_range("2020-01-01", periods=10, freq="YS")
        data_series = pd.Series([4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0], index=dates)
        
        mock_instance.get_series.return_value = data_series
        mock_instance.search.return_value = pd.DataFrame({"id": ["TEST_ID"]}, index=["TEST_ID"])
        
        result = fetch_regional_macro_stats(["Austin-Round Rock"])
        data = json.loads(result)
        
        assert len(data) > 0
        # The skill might return 'City' instead of 'Region' now
        assert data[0].get("Region") == "Austin-Round Rock" or data[0].get("City") == "Austin-Round Rock"
        assert "Unemployment Rate" in data[0]

def test_eia_electricity_rates(mock_env):
    """Test successful retrieval of EIA electricity rates."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "response": {"data": [{"price": 10.5, "period": "2024-01", "stateid": "TX"}]}
        }
        
        result = fetch_state_electricity_rates(["TX"], sector="industrial")
        data = json.loads(result)
        
        assert data[0]["State"] == "TX"
        assert any(k in data[0] for k in ["Avg Price (cents/kWh)", "Electricity Rate"])

def test_sentiment_analysis(mock_env):
    """Test news sentiment retrieval."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "articles": [{"title": "Major Tech Move to Austin", "source": {"name": "TechNews"}, "publishedAt": "2024-03-24", "description": "Details..."}]
        }
        
        result = analyze_market_sentiment("Austin tech news")
        data = json.loads(result)
        
        assert len(data) == 1
        assert "Austin" in data[0]["Title"]

def test_climate_risk_index():
    """Test FEMA NRI grounded benchmarks."""
    result = get_climate_risk_index(["Austin", "Miami"])
    data = json.loads(result)
    
    assert data[0]["City"] == "Austin"
    assert data[1]["City"] == "Miami"

def test_logistics_efficiency():
    """Test DOT logistics strategy benchmarks."""
    result = get_logistics_efficiency(["Raleigh"])
    data = json.loads(result)
    
    assert data[0]["City"] == "Raleigh"
    assert "Intermodal Hub Access" in data[0]

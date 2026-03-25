#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ADK Skill: Real-Time Market Sentiment (NewsAPI)."""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

class SentimentRequest(BaseModel):
    query: str = Field(..., description="Query to search for news sentiment (e.g. 'Austin labor market' or 'Raleigh economic growth').")
    language: str = Field("en", description="Language for news search.")


def analyze_market_sentiment(
    query: str,
    language: str = "en"
) -> str:
    """
    Fetches real-time news headlines to perform sentiment analysis on MSAs and industries.
    Use this to catch 'Soft Signals' (strikes, recent large relocations, political decisions)
    that governemnt data (BLS/Census) might have missed.
    """
    if not NEWS_API_KEY:
        return "ERROR: NEWS_API_KEY is not set in environment variables."

    # NewsAPI endpoint for top headlines or everything. 
    # 'everything' allows for more specific query matching.
    url = f"https://newsapi.org/v2/everything?q={query}&language={language}&sortBy=relevancy&pageSize=8&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=12)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return f"No recent news found for query: {query}."
                
            results = []
            for art in articles:
                results.append({
                    "Title": art["title"],
                    "Source": art["source"]["name"],
                    "PublishedAt": art["publishedAt"],
                    "Description": art["description"][:150] + "..." if art["description"] else "N/A"
                })
            
            # The Scribe node or LLM will perform the final sentiment weighting on these results.
            return json.dumps(results, indent=2)
        else:
            return f"Error from NewsAPI: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Request failed: {str(e)}"

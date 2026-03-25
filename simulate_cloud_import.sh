#!/bin/bash
# Simulates the cloud environment where NO API keys are set in the environment
# during module import time.

echo "🔍 Simulating fresh cloud import without environment variables..."

# Unset all standard keys
unset FRED_API_KEY
unset BEA_API_KEY
unset CENSUS_API_KEY
unset HUD_API_KEY
unset FEC_API_KEY
unset NEWS_API_KEY
unset EIA_API_KEY

# Run the import check
uv run --project /Users/enriq/Documents/git/economic_research_agent/pyproject.toml python3 -c "import economic_research_agent.agent"

if [ $? -eq 0 ]; then
    echo "✅ Success: The agent module imports cleanly without environment variables!"
else
    echo "❌ Failure: The agent module crashed during import without environment variables."
fi

#!/bin/bash
# Script to create Secret Manager secrets from .env file

# Exit on error
set -e

PROJECT_ID="project-maui"

create_secret() {
    local name=$1
    local value=$2
    
    echo "Processing $name..."
    
    # Check if secret exists
    if gcloud secrets describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "Secret $name already exists."
    else
        echo "Creating secret $name..."
        gcloud secrets create "$name" --replication-policy="automatic" --project="$PROJECT_ID"
    fi
    
    # Add version
    echo -n "$value" | gcloud secrets versions add "$name" --data-file=- --project="$PROJECT_ID"
    echo "Added version for $name."
}

# Read .env and process keys
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.* ]] && continue
    [[ -z "$key" ]] && continue
    
    # Process specific keys
    case "$key" in
        GEMINI_API_KEY|BEA_API_KEY|FRED_API_KEY|CENSUS_API_KEY|EIA_API_KEY|BLS_API_KEY|NEWS_API_KEY|HUD_API_KEY|FEC_API_KEY|SERPER_API_KEY|CDC_APP_TOKEN|OPENFDA_API_KEY)
            create_secret "$key" "$value"
            ;;
    esac
done < /Users/enriq/Documents/git/economic_research_agent/.env

echo "All secrets processed."

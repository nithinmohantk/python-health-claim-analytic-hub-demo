#!/bin/bash

# GitHub Rulesets Import Script
# This script imports all rulesets into your GitHub repository

set -e

# Configuration
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
REPO_OWNER="${REPO_OWNER:-}"
REPO_NAME="${REPO_NAME:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}Error: GITHUB_TOKEN environment variable is not set${NC}"
    echo "Please set it with: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

if [ -z "$REPO_OWNER" ]; then
    echo -e "${RED}Error: REPO_OWNER environment variable is not set${NC}"
    echo "Please set it with: export REPO_OWNER=your_username"
    exit 1
fi

if [ -z "$REPO_NAME" ]; then
    echo -e "${RED}Error: REPO_NAME environment variable is not set${NC}"
    echo "Please set it with: export REPO_NAME=your_repo_name"
    exit 1
fi

# API endpoint
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/rulesets"

# Headers
HEADERS=(
    -H "Authorization: token $GITHUB_TOKEN"
    -H "Accept: application/vnd.github+json"
    -H "X-GitHub-Api-Version: 2022-11-28"
    -H "Content-Type: application/json"
)

# Ruleset files
RULESETS=(
    "main-branch-protection.json"
    "develop-branch-protection.json"
    "branch-naming-convention.json"
)

echo -e "${YELLOW}Importing GitHub Rulesets...${NC}"
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Function to import a ruleset
import_ruleset() {
    local file=$1
    local filepath=".github/rulesets/$file"
    
    if [ ! -f "$filepath" ]; then
        echo -e "${RED}Error: File $filepath not found${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Importing $file...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        "${HEADERS[@]}" \
        "$API_URL" \
        -d @"$filepath")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ Successfully imported $file${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to import $file${NC}"
        echo "HTTP Code: $http_code"
        echo "Response: $body"
        return 1
    fi
}

# Import all rulesets
success_count=0
fail_count=0

for ruleset in "${RULESETS[@]}"; do
    if import_ruleset "$ruleset"; then
        ((success_count++))
    else
        ((fail_count++))
    fi
    echo ""
done

# Summary
echo -e "${YELLOW}Import Summary:${NC}"
echo -e "${GREEN}Success: $success_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All rulesets imported successfully!${NC}"
    exit 0
else
    echo -e "${RED}Some rulesets failed to import${NC}"
    exit 1
fi

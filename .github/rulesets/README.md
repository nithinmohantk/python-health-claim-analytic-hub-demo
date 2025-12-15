# GitHub Rulesets - Import Guide

This directory contains JSON ruleset files ready to import into GitHub for branch protection and naming conventions.

## Files Overview

- **`main-branch-protection.json`** - Protection rules for `main` branch
- **`develop-branch-protection.json`** - Protection rules for `develop` branch
- **`branch-naming-convention.json`** - Branch naming pattern enforcement
- **`all-rulesets.json`** - Combined rulesets for bulk import

## Import Methods

### Method 1: GitHub Web UI (Recommended)

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Rules** → **Rulesets**
3. Click **"New ruleset"** → **"Import a ruleset"**
4. Upload the JSON file you want to import
5. Review the ruleset configuration
6. Click **"Create ruleset"**

### Method 2: GitHub CLI (gh)

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate
gh auth login

# Import main branch protection
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input .github/rulesets/main-branch-protection.json

# Import develop branch protection
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input .github/rulesets/develop-branch-protection.json

# Import branch naming convention
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input .github/rulesets/branch-naming-convention.json
```

### Method 3: GitHub API (curl)

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_token_here
export REPO_OWNER=your_username
export REPO_NAME=your_repo_name

# Import main branch protection
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/rulesets \
  -d @.github/rulesets/main-branch-protection.json

# Import develop branch protection
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/rulesets \
  -d @.github/rulesets/develop-branch-protection.json

# Import branch naming convention
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/rulesets \
  -d @.github/rulesets/branch-naming-convention.json
```

### Method 4: Python Script

```python
import json
import requests

GITHUB_TOKEN = "your_token_here"
REPO_OWNER = "your_username"
REPO_NAME = "your_repo_name"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

base_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/rulesets"

rulesets = [
    ".github/rulesets/main-branch-protection.json",
    ".github/rulesets/develop-branch-protection.json",
    ".github/rulesets/branch-naming-convention.json"
]

for ruleset_file in rulesets:
    with open(ruleset_file, 'r') as f:
        ruleset_data = json.load(f)
    
    response = requests.post(base_url, headers=headers, json=ruleset_data)
    
    if response.status_code == 201:
        print(f"✅ Successfully imported {ruleset_file}")
    else:
        print(f"❌ Failed to import {ruleset_file}: {response.text}")
```

## Ruleset Details

### Main Branch Protection

**Applies to:** `main` branch

**Protections:**
- ✅ Requires 1 approving review
- ✅ Requires status checks: test (3.10, 3.11, 3.12), docker-build
- ✅ Requires branches to be up to date
- ✅ Requires conversation resolution
- ✅ Blocks force pushes
- ✅ Blocks branch deletion
- ✅ Blocks direct pushes (PRs only)

### Develop Branch Protection

**Applies to:** `develop` branch

**Protections:**
- ✅ Requires 1 approving review
- ✅ Requires status checks: test (3.10), lint
- ✅ Requires branches to be up to date
- ✅ Requires conversation resolution
- ✅ Blocks force pushes
- ✅ Blocks branch deletion

### Branch Naming Convention

**Applies to:** All branches except `main` and `develop`

**Allowed Patterns:**
- `feature/description`
- `bugfix/description`
- `hotfix/description`
- `release/version`
- `docs/description`
- `refactor/description`
- `test/description`

## Customization

Before importing, you may want to customize:

1. **Status Check Names**: Update `required_status_checks` contexts to match your actual CI workflow names
2. **Review Requirements**: Adjust `required_approving_review_count` if you need more approvals
3. **Code Owners**: Set `require_code_owner_review: true` if you have a CODEOWNERS file
4. **Bypass Actors**: Add users/teams to `bypass_actors` array if needed (not recommended)

## Verification

After importing, verify the rulesets:

1. Go to **Settings** → **Rules** → **Rulesets**
2. Check that all three rulesets are listed and active
3. Test by creating a PR to `main` or `develop`
4. Verify that protection rules are enforced

## Troubleshooting

### Status Checks Not Found

If you see errors about missing status checks:
1. Check your workflow file names in `.github/workflows/`
2. Update the `context` values in the JSON to match your actual check names
3. Run a test workflow to see the exact check names

### API Errors

If you get API errors:
1. Verify your GitHub token has `repo` scope
2. Check that you have admin access to the repository
3. Ensure the JSON is valid (use a JSON validator)

### Rules Not Applying

If rules aren't being enforced:
1. Check that `enforcement` is set to `"active"`
2. Verify the branch patterns in `conditions.ref_name.include`
3. Ensure the ruleset is not in bypass mode

## Updating Rulesets

To update an existing ruleset:

1. Export current ruleset via API or UI
2. Modify the JSON file
3. Update via API (PUT request) or delete and recreate

```bash
# Get ruleset ID first
gh api repos/:owner/:repo/rulesets

# Update ruleset
gh api repos/:owner/:repo/rulesets/:ruleset_id \
  --method PUT \
  --input .github/rulesets/main-branch-protection.json
```

## References

- [GitHub Rulesets API](https://docs.github.com/en/rest/repos/rules)
- [Managing Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

---

**Last Updated**: 2025-11-02

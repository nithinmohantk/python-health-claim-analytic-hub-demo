# GitHub Flow Guide

This repository follows the **GitHub Flow** branching strategy for collaborative development.

## Overview

GitHub Flow is a lightweight, branch-based workflow designed around regular deployments. It's perfect for projects that deploy regularly.

## Branch Structure

```
main (production-ready)
  ↑
  │ Merge via PR
  │
develop (integration branch)
  ↑
  │ Merge via PR
  │
feature/branch-name (development)
```

## Workflow Steps

### 1. Start from Main/Develop

Always start from an up-to-date base branch:

```bash
# For new features
git checkout develop
git pull origin develop

# For hotfixes (production issues)
git checkout main
git pull origin main
```

### 2. Create a Feature Branch

Create a descriptive branch name following conventions:

```bash
# Feature
git checkout -b feature/add-user-authentication

# Bug fix
git checkout -b bugfix/fix-api-timeout

# Hotfix
git checkout -b hotfix/critical-security-patch

# Documentation
git checkout -b docs/update-api-docs
```

### 3. Make Changes

Work on your feature, making small, focused commits:

```bash
# Make changes
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: user authentication module"
```

**Commit Message Format:**
- `Add: description` - New feature
- `Fix: description` - Bug fix
- `Update: description` - Update existing feature
- `Refactor: description` - Code refactoring
- `Docs: description` - Documentation changes
- `Test: description` - Test additions/changes
- `Style: description` - Code style changes

### 4. Push and Create Pull Request

Push your branch and create a PR:

```bash
# Push branch
git push origin feature/your-feature-name
```

Then:
1. Go to GitHub
2. Click "New Pull Request"
3. Select base branch (`develop` or `main`)
4. Select your feature branch
5. Fill out PR template
6. Request reviews

### 5. Code Review

During review:
- ✅ Address review comments
- ✅ Make requested changes
- ✅ Push updates to your branch
- ✅ Ensure all CI checks pass
- ✅ Resolve conversations

### 6. Merge

Once approved:
- **Squash and merge** - Recommended for feature branches
- **Merge commit** - For release branches
- **Rebase and merge** - For small, single-commit changes

### 7. Clean Up

After merging:
- Delete the feature branch (GitHub will prompt)
- Update local branches:

```bash
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
```

## Branch Types

### Feature Branches

**Purpose**: New features or enhancements

**Naming**: `feature/description`

**Example**:
```bash
feature/add-anomaly-detection
feature/improve-network-visualization
```

**Lifecycle**: Created → Developed → PR → Merged → Deleted

### Bug Fix Branches

**Purpose**: Fix bugs in develop/main

**Naming**: `bugfix/description`

**Example**:
```bash
bugfix/fix-data-validation-error
bugfix/resolve-api-timeout-issue
```

**Base**: Usually `develop`, sometimes `main`

### Hotfix Branches

**Purpose**: Critical production fixes

**Naming**: `hotfix/description`

**Example**:
```bash
hotfix/critical-security-patch
hotfix/fix-production-bug
```

**Base**: `main` (then merge back to `develop`)

### Release Branches

**Purpose**: Prepare for release

**Naming**: `release/version`

**Example**:
```bash
release/v1.2.0
release/v2.0.0-beta
```

**Base**: `develop`

## Pull Request Process

### PR Requirements

- ✅ Descriptive title (follows convention)
- ✅ Detailed description (minimum 50 characters)
- ✅ Link to related issues
- ✅ All CI checks passing
- ✅ At least 1 approval
- ✅ No merge conflicts
- ✅ Code follows style guidelines

### PR Template

Use the PR template (`.github/pull_request_template.md`) to ensure all information is provided.

### Review Checklist

Before requesting review:
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Security considerations addressed

## Best Practices

### Commit Often

Make small, focused commits:
```bash
# Good: Small, focused commits
git commit -m "Add: user authentication module"
git commit -m "Add: password validation"
git commit -m "Test: add auth unit tests"

# Avoid: Large, vague commits
git commit -m "Update stuff"
```

### Keep Branches Up to Date

Regularly sync with base branch:
```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature
git merge develop
# or
git rebase develop
```

### Write Good Commit Messages

Follow the convention:
- Start with type: `Add:`, `Fix:`, `Update:`, etc.
- Be descriptive but concise
- Explain "what" and "why" if needed

### Keep PRs Focused

- One feature per PR
- Keep changes small (< 1000 lines if possible)
- Split large features into multiple PRs

### Test Before Pushing

```bash
# Run tests locally
make test

# Check linting
make lint

# Format code
make format
```

## Common Scenarios

### Updating Your Branch

```bash
# Fetch latest changes
git fetch origin

# Update develop
git checkout develop
git pull origin develop

# Update your feature branch
git checkout feature/your-feature
git merge develop
# or rebase: git rebase develop
```

### Fixing Review Comments

```bash
# Make changes
# ...

# Commit fixes
git add .
git commit -m "Fix: address review comments"

# Push updates
git push origin feature/your-feature
```

### Resolving Merge Conflicts

```bash
# Update branch
git checkout feature/your-feature
git merge develop

# Resolve conflicts in files
# Edit conflicted files
# ...

# Stage resolved files
git add .

# Complete merge
git commit -m "Merge: resolve conflicts with develop"
```

### Emergency Hotfix

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Make fix
# ...

# Commit and push
git add .
git commit -m "Fix: critical production issue"
git push origin hotfix/critical-fix

# Create PR to main
# After merge, merge main back to develop
```

## Automation

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Hooks will automatically:
- Format code (black, isort)
- Check linting (flake8)
- Run type checking (mypy)

### CI/CD Checks

GitHub Actions automatically:
- Run tests on multiple Python versions
- Check code formatting
- Run linting
- Build Docker image
- Validate branch names
- Check PR quality

## Troubleshooting

### PR Checks Failing

1. Check the failing check details
2. Fix issues locally
3. Push fixes to your branch
4. Checks will re-run automatically

### Can't Push to Protected Branch

Protected branches (`main`, `develop`) require PRs:
- Don't push directly
- Create a feature branch
- Open a PR

### Merge Conflicts

1. Update your branch: `git pull origin develop`
2. Resolve conflicts locally
3. Test the merge
4. Push resolved changes

## Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Branch Protection Rules](.github/BRANCH_PROTECTION.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Questions?** Open an issue or check the documentation!

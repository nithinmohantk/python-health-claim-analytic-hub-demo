# Branch Protection Rules & GitHub Flow

This document outlines the branch protection rules and GitHub Flow implementation for this repository.

## Branch Protection Rules

### Main Branch (`main`)

**Protection Settings:**
- ✅ **Require pull request reviews before merging**
  - Required approving reviews: **1**
  - Dismiss stale pull request approvals when new commits are pushed: **Yes**
  - Require review from Code Owners: **No** (can be enabled if CODEOWNERS file exists)
  
- ✅ **Require status checks to pass before merging**
  - Required status checks:
    - `test / test (3.10)`
    - `test / test (3.11)`
    - `test / test (3.12)`
    - `test / docker-build`
  - Require branches to be up to date before merging: **Yes**
  
- ✅ **Require conversation resolution before merging**: **Yes**
  
- ✅ **Require signed commits**: **No** (optional, can be enabled)
  
- ✅ **Require linear history**: **No** (allows merge commits)
  
- ✅ **Include administrators**: **No** (admins must follow rules)
  
- ✅ **Restrict who can push to matching branches**: **No** (use PRs only)
  
- ✅ **Allow force pushes**: **No**
  
- ✅ **Allow deletions**: **No**

### Develop Branch (`develop`)

**Protection Settings:**
- ✅ **Require pull request reviews before merging**
  - Required approving reviews: **1**
  
- ✅ **Require status checks to pass before merging**
  - Required status checks:
    - `test / test (3.10)`
    - `test / lint`
  - Require branches to be up to date before merging: **Yes**
  
- ✅ **Require conversation resolution before merging**: **Yes**
  
- ✅ **Allow force pushes**: **No**
  
- ✅ **Allow deletions**: **No**

## Branch Naming Conventions

### Feature Branches
```
feature/description-of-feature
feature/add-user-authentication
feature/improve-anomaly-detection
```

### Bug Fix Branches
```
bugfix/description-of-bug
bugfix/fix-api-timeout-error
bugfix/resolve-data-validation-issue
```

### Hotfix Branches
```
hotfix/critical-security-patch
hotfix/fix-production-bug
```

### Release Branches
```
release/v1.2.0
release/v2.0.0-beta
```

### Documentation Branches
```
docs/update-readme
docs/add-api-documentation
```

### Refactoring Branches
```
refactor/modularize-data-module
refactor/improve-error-handling
```

## GitHub Flow Implementation

### Workflow Overview

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

### Step-by-Step Process

#### 1. Create a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/your-bug-description
```

#### 2. Make Changes and Commit

```bash
# Make your changes
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: feature description"
# or
git commit -m "Fix: bug description"
```

**Commit Message Format:**
- `Add: description` - New feature
- `Fix: description` - Bug fix
- `Update: description` - Update existing feature
- `Refactor: description` - Code refactoring
- `Docs: description` - Documentation changes
- `Test: description` - Test additions/changes
- `Style: description` - Code style changes

#### 3. Push and Create Pull Request

```bash
# Push branch to remote
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub:
- **Base branch**: `develop` (or `main` for hotfixes)
- **Compare branch**: `feature/your-feature-name`
- Fill out PR template
- Request review from team members

#### 4. Code Review Process

- ✅ All CI checks must pass
- ✅ At least 1 approval required
- ✅ No merge conflicts
- ✅ All conversations resolved
- ✅ Code follows style guidelines

#### 5. Merge Pull Request

Once approved:
- Use **"Squash and merge"** for feature branches
- Use **"Merge commit"** for release branches
- Use **"Rebase and merge"** for small, single-commit changes

#### 6. Delete Branch After Merge

After merging, delete the feature branch:
- ✅ Delete branch button in GitHub PR
- Or manually: `git push origin --delete feature/your-feature-name`

## Pull Request Requirements

### Required Checks

All PRs must pass:
1. ✅ **Linting** (flake8)
2. ✅ **Code Formatting** (black, isort)
3. ✅ **Type Checking** (mypy)
4. ✅ **Tests** (pytest with coverage)
5. ✅ **Docker Build** (if applicable)

### PR Template Requirements

- Clear title describing the change
- Description of what and why
- Link to related issues
- Screenshots (for UI changes)
- Testing instructions
- Checklist of requirements

## Status Checks Configuration

### Required Status Checks

These checks must pass before merging:

| Check Name | Description | Required For |
|------------|-------------|--------------|
| `test / test (3.10)` | Python 3.10 tests | main, develop |
| `test / test (3.11)` | Python 3.11 tests | main |
| `test / test (3.12)` | Python 3.12 tests | main |
| `test / lint` | Code linting | main, develop |
| `test / docker-build` | Docker build | main |

### Optional Checks

These checks provide information but don't block merges:
- Coverage reporting
- Type checking (mypy)
- Security scanning

## Emergency Procedures

### Hotfix Process

For critical production issues:

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# Make fix and commit
git add .
git commit -m "Fix: critical production issue"

# Push and create PR to main
git push origin hotfix/critical-issue
```

After merging hotfix to `main`:
1. Merge `main` back to `develop`
2. Tag the release: `git tag v1.2.1`
3. Deploy to production

### Bypassing Protection (Admin Only)

In extreme emergencies, admins can temporarily bypass protection:
1. Go to branch settings
2. Temporarily disable protection
3. Make emergency fix
4. Re-enable protection immediately
5. Document the bypass in an issue

## Branch Lifecycle

### Feature Branch Lifecycle

```
Created → Development → PR Opened → Review → Approved → Merged → Deleted
```

### Branch Retention Policy

- **Active branches**: Keep indefinitely
- **Merged branches**: Delete after 30 days
- **Stale branches**: Delete after 90 days of inactivity

## Automation

### GitHub Actions Integration

Branch protection is enforced via:
- `.github/workflows/ci.yml` - Main CI pipeline
- Status checks are automatically required
- PR comments with check results

### Pre-commit Hooks

Local development uses pre-commit hooks:
- Automatic formatting
- Linting checks
- Type checking

Install: `pre-commit install`

## Compliance & Security

### Security Requirements

- ✅ No secrets in code
- ✅ Dependencies scanned for vulnerabilities
- ✅ Code review required
- ✅ Security-sensitive changes require additional review

### Compliance Checklist

Before merging:
- [ ] No hardcoded secrets
- [ ] Dependencies up to date
- [ ] Security best practices followed
- [ ] HIPAA considerations addressed (if applicable)
- [ ] Documentation updated

## Troubleshooting

### PR Checks Failing

1. Check the failing check details
2. Fix issues locally
3. Push fixes to the branch
4. Checks will re-run automatically

### Merge Conflicts

1. Update your branch: `git pull origin develop`
2. Resolve conflicts locally
3. Test the merge
4. Push resolved changes

### Branch Protection Errors

If you see "branch is protected" errors:
- Ensure you're using PRs (not direct push)
- Check that all required checks pass
- Verify you have required approvals

## References

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Last Updated**: 2025-11-02  
**Maintained By**: Development Team

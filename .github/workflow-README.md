# GitHub Configuration

This directory contains GitHub-specific configuration files for branch protection, workflows, and repository management.

## Files Overview

### Branch Protection & Workflow

- **`BRANCH_PROTECTION.md`** - Complete branch protection rules and policies
- **`GITHUB_FLOW.md`** - GitHub Flow implementation guide
- **`pull_request_template.md`** - PR template for consistent pull requests

### Workflows

- **`workflows/ci.yml`** - Main CI/CD pipeline (testing, linting, type checking)
- **`workflows/branch-protection.yml`** - Branch naming and protection checks
- **`workflows/pr-checks.yml`** - PR quality and validation checks

### Issue Templates

- **`ISSUE_TEMPLATE/bug_report.md`** - Bug report template
- **`ISSUE_TEMPLATE/feature_request.md`** - Feature request template
- **`ISSUE_TEMPLATE/config.yml`** - Issue template configuration

### Code Ownership

- **`CODEOWNERS`** - Defines code owners for automatic review requests

## Quick Start

### Setting Up Branch Protection

1. Go to repository Settings → Branches
2. Add rule for `main` branch
3. Configure according to `.github/BRANCH_PROTECTION.md`
4. Add rule for `develop` branch (optional)

### Using GitHub Flow

1. Read `.github/GITHUB_FLOW.md` for complete workflow
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and commit
4. Push and create PR using the template
5. Wait for reviews and CI checks
6. Merge when approved

### Creating Pull Requests

When creating a PR, the template (`.github/pull_request_template.md`) will automatically populate. Fill out all sections:

- Description of changes
- Type of change
- Related issues
- Testing performed
- Checklist items

## Branch Protection Rules Summary

### Main Branch
- ✅ Requires PR reviews (1 approval)
- ✅ Requires CI checks to pass
- ✅ Requires conversation resolution
- ✅ No force pushes
- ✅ No deletions

### Develop Branch
- ✅ Requires PR reviews (1 approval)
- ✅ Requires basic CI checks
- ✅ Requires conversation resolution
- ✅ No force pushes

## Automated Checks

### On Every PR

- ✅ Branch name validation
- ✅ Commit message format check
- ✅ PR description validation
- ✅ Code quality checks (linting, formatting)
- ✅ Test execution
- ✅ Docker build verification
- ✅ Secret scanning

### On Every Push

- ✅ CI pipeline execution
- ✅ Test coverage reporting

## Branch Naming Conventions

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical production fixes
- `release/version` - Release preparation
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## Code Review Process

1. **Create PR** - Use template, link issues
2. **CI Checks** - Wait for all checks to pass
3. **Request Review** - Tag reviewers or use CODEOWNERS
4. **Address Feedback** - Make changes, push updates
5. **Approval** - Get required approvals
6. **Merge** - Use appropriate merge strategy

## Security

- ✅ Secret scanning on all PRs
- ✅ Dependency vulnerability scanning
- ✅ Code review required
- ✅ Protected branches
- ✅ Signed commits (optional)

## Resources

- [Branch Protection Guide](BRANCH_PROTECTION.md)
- [GitHub Flow Guide](GITHUB_FLOW.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [GitHub Docs](https://docs.github.com)

---

**Last Updated**: 2025-11-02

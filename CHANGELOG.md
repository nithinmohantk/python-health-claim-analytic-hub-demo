# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD workflow for automated testing
- Pre-commit hooks configuration
- Makefile for common development tasks
- CONTRIBUTING.md guide
- SECURITY.md policy
- .editorconfig for consistent formatting
- .dockerignore for optimized Docker builds
- Proper logging module (replacing debug statements)

### Changed
- Removed debug statements from production code
- Improved error handling and logging
- Enhanced type hints throughout codebase

### Fixed
- Duplicate entries in .gitignore
- Missing LICENSE file
- Missing .env.example template

## [1.0.0] - 2025-11-02

### Added
- Initial release of HealthClaim Analytics Hub
- Streamlit web application for healthcare claims analysis
- Data loading and validation from CSV/GitHub
- Patient-provider network visualization with Plotly
- Three anomaly detection methods:
  - Threshold-based detection
  - Statistical Z-Score detection
  - Isolation Forest ML detection
- GPT-4 integration for:
  - Anomaly explanation generation
  - Network insights analysis
  - Q&A interface
- Comprehensive test suite (86 tests)
- Docker and docker-compose support
- Extensive documentation

### Security
- API key management via Streamlit secrets
- Data validation and sanitization
- HIPAA-aware data handling

## [0.0.1-alpha] - 2025-11-01

### Added
- Initial project setup
- Basic Streamlit application structure
- Core utility modules

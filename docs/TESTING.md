# 🧪 HealthClaim Analytics Hub - Testing Guide & Coverage Report

## Overview

This document provides guidance on testing the HealthClaim Analytics Hub application and outlines the test suite structure.

## Test Coverage Strategy

### Testing Approach
- **Unit Tests**: Individual function testing
- **Integration Tests**: Component interaction testing  
- **Mocking**: External dependencies (OpenAI API, GitHub data)
- **Coverage Target**: >60% code coverage

## Test Suite Structure

### Test Files

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_data.py         # Data module tests
├── test_network.py      # Network analysis tests
├── test_anomaly.py      # Anomaly detection tests
└── test_gpt.py          # GPT integration tests
```

## Fixtures Available

### Data Fixtures (conftest.py)

#### `sample_claims_df`
- 5 sample healthcare claims
- Includes: patient_id, provider_id, claim_amount, diagnosis_code, procedure_code, date
- Used for: Basic functionality testing

#### `large_claims_df`
- 1000 synthetic claims
- Used for: Performance and scalability testing

#### `empty_claims_df`
- Empty DataFrame with correct schema
- Used for: Edge case and error handling

#### `claims_with_nulls`
- DataFrame with NULL values
- Used for: Validation and sanitization testing

### Network Fixtures

#### `sample_network`
- Simple patient-provider network (2 patients, 2 providers)
- Used for: Network analysis testing

#### `dense_network`
- Dense network with clique-like structures
- Used for: Fraud ring detection testing

### Anomaly Fixtures

#### `anomaly_results`
- Sample DataFrame with anomaly flags and scores
- Used for: Anomaly result analysis testing

## Test Files Details

### tests/test_data.py
Tests for `utils/data.py` module:
- ✅ Data loading and caching
- ✅ CSV parsing and validation
- ✅ Data sanitization
- ✅ Filtering operations
- ✅ Statistical calculations
- ✅ Error handling

### tests/test_network.py
Tests for `utils/network.py` module:
- ✅ Network construction from claims
- ✅ Network visualization generation
- ✅ Network metrics calculation
- ✅ Clique/cluster detection
- ✅ Node and edge creation
- ✅ Layout optimization

### tests/test_anomaly.py
Tests for `utils/anomaly.py` module:
- ✅ Threshold-based detection
- ✅ Z-score based detection
- ✅ Isolation Forest detection
- ✅ Frequency-based detection
- ✅ Score combination
- ✅ Anomaly ranking
- ✅ Summary statistics

### tests/test_gpt.py
Tests for `utils/gpt.py` module:
- ✅ API initialization
- ✅ Anomaly explanation generation (mocked)
- ✅ Network insights generation (mocked)
- ✅ Q&A functionality (mocked)
- ✅ API connection validation
- ✅ Error handling (auth, rate limits)

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_data.py -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=utils --cov-report=html --cov-report=term-missing
```

### Run Specific Markers
```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run tests related to data
pytest tests/ -m data

# Skip slow tests
pytest tests/ -m "not slow"
```

### Run with Detailed Output
```bash
pytest tests/ -vv --tb=long --capture=no
```

## Code Coverage Goals

### Target Coverage by Module

| Module | Target | Method |
|--------|--------|--------|
| `utils/data.py` | 80% | Load, validate, filter operations |
| `utils/network.py` | 75% | Network building, visualization |
| `utils/anomaly.py` | 80% | Detection algorithms, scoring |
| `utils/gpt.py` | 70% | API calls (mostly mocked) |
| **Overall** | **70%** | All modules combined |

### Coverage Report Generation

After running tests with coverage:

```bash
# View coverage report in terminal
pytest --cov=utils --cov-report=term-missing

# Generate HTML report
pytest --cov=utils --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML report (for CI/CD)
pytest --cov=utils --cov-report=xml
```

## Test Markers

### Available Markers
```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow         # Slow running tests
@pytest.mark.mock         # Tests using mocks
@pytest.mark.data         # Data module tests
@pytest.mark.network      # Network module tests
@pytest.mark.anomaly      # Anomaly module tests
@pytest.mark.gpt          # GPT module tests
```

### Using Markers
```bash
# Run only data tests
pytest -m data

# Run everything except slow tests
pytest -m "not slow"

# Run tests matching multiple markers
pytest -m "unit and data"
```

## Continuous Integration

### GitHub Actions Workflow Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=utils --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Writing New Tests

### Test Template
```python
import pytest
from utils.module_name import function_name

class TestFunctionName:
    """Test suite for function_name"""
    
    def test_basic_functionality(self, sample_claims_df):
        """Test basic functionality with happy path"""
        result = function_name(sample_claims_df)
        assert result is not None
        assert len(result) > 0
    
    def test_with_empty_data(self, empty_claims_df):
        """Test behavior with empty DataFrame"""
        result = function_name(empty_claims_df)
        assert result.empty
    
    def test_with_invalid_input(self):
        """Test behavior with invalid inputs"""
        with pytest.raises(ValueError):
            function_name(None)
    
    @pytest.mark.slow
    def test_performance(self, large_claims_df):
        """Test performance with large dataset"""
        import time
        start = time.time()
        result = function_name(large_claims_df)
        elapsed = time.time() - start
        assert elapsed < 5.0  # Should complete in <5 seconds
```

## Debugging Tests

### Run Single Test with Print Statements
```bash
pytest tests/test_data.py::TestLoadData::test_basic_loading -v -s
```

### Debug with PDB
```bash
pytest tests/test_data.py --pdb
# Or on failure:
pytest tests/test_data.py --pdb-on-error
```

### Verbose Output
```bash
pytest tests/ -vv --tb=long --capture=no
```

## Performance Testing

### Benchmark Tests
```python
def test_load_performance(benchmark, sample_claims_df):
    """Benchmark data loading performance"""
    result = benchmark(load_claims_data_func, sample_claims_df)
    assert result is not None
```

### Time Measurement
```bash
pytest tests/ --durations=10  # Show 10 slowest tests
```

## Mocking Best Practices

### Mock External APIs
```python
@pytest.mark.mock
def test_gpt_call(mocker):
    """Test GPT call with mocked API"""
    mock_response = {"choices": [{"message": {"content": "Test"}}]}
    mocker.patch('openai.ChatCompletion.create', return_value=mock_response)
    
    result = generate_anomaly_explanation(claim_row)
    assert result == "Test"
```

### Mock Environment Variables
```python
def test_with_env_var(monkeypatch):
    """Test with mocked environment variable"""
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    # Run test
```

## Troubleshooting

### Common Issues

**Q: Tests fail with "No module named streamlit"**
A: Install dependencies:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

**Q: Coverage is lower than expected**
A: Check if tests are discovering all code paths:
```bash
pytest --cov=utils --cov-report=term-missing
```

**Q: Test timeouts**
A: Increase timeout in pytest.ini or for specific test:
```python
@pytest.mark.timeout(60)
def test_slow_function():
    pass
```

## Best Practices

✅ **Do**
- Write tests for edge cases
- Use descriptive test names
- Mock external dependencies
- Keep tests independent
- Use fixtures for setup
- Test error conditions

❌ **Don't**
- Test implementation details
- Make tests interdependent
- Use random data without seeds
- Skip slow tests in CI/CD
- Commit failing tests
- Mock too much

## Resources

- [Pytest Documentation](https://docs.pytest.org)
- [Pytest-cov](https://pytest-cov.readthedocs.io)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Next Steps

1. ✅ Review existing tests in `tests/` folder
2. ✅ Run full test suite: `pytest tests/ -v`
3. ✅ Generate coverage: `pytest --cov=utils --cov-report=html`
4. ✅ Review coverage report: `open htmlcov/index.html`
5. ✅ Add more tests for uncovered code
6. ✅ Set up CI/CD with automated testing

---

**Last Updated**: November 2, 2025  
**Test Framework**: Pytest  
**Target Coverage**: 70%+  
**Python Version**: 3.10+

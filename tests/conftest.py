"""
Pytest configuration and shared fixtures for HealthClaim Analytics Hub tests

This file contains:
- Pytest configuration hooks
- Shared test fixtures
- Mock utilities
- Sample data generators
"""

import pytest
import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ==================== FIXTURES: Sample Data ====================

@pytest.fixture
def sample_claims_df():
    """
    Provides a sample claims DataFrame for testing
    
    Returns:
        pd.DataFrame with 5 sample claims
    """
    return pd.DataFrame({
        'patient_id': [101, 102, 103, 104, 105],
        'provider_id': [501, 502, 501, 503, 502],
        'claim_amount': [1000.0, 2500.0, 1500.0, 5000.0, 2000.0],
        'diagnosis_code': ['I10', 'E11', 'J45', 'I50', 'F41'],
        'procedure_code': ['99213', '99214', '99215', '99213', '99214'],
        'date': pd.date_range('2023-01-01', periods=5)
    })


@pytest.fixture
def large_claims_df():
    """
    Provides a larger claims DataFrame for performance testing
    
    Returns:
        pd.DataFrame with 1000 sample claims
    """
    np_import = pytest.importorskip("numpy")
    
    dates = pd.date_range('2023-01-01', periods=1000, freq='D')
    return pd.DataFrame({
        'patient_id': np_import.random.randint(100, 500, 1000),
        'provider_id': np_import.random.randint(500, 700, 1000),
        'claim_amount': np_import.random.uniform(500, 5000, 1000),
        'diagnosis_code': np_import.random.choice(['I10', 'E11', 'J45', 'I50', 'F41'], 1000),
        'procedure_code': np_import.random.choice(['99213', '99214', '99215', '99216'], 1000),
        'date': dates
    })


@pytest.fixture
def empty_claims_df():
    """
    Provides an empty claims DataFrame for error testing
    
    Returns:
        pd.DataFrame with no rows but correct columns
    """
    return pd.DataFrame({
        'patient_id': pd.Series([], dtype=int),
        'provider_id': pd.Series([], dtype=int),
        'claim_amount': pd.Series([], dtype=float),
        'diagnosis_code': pd.Series([], dtype=str),
    })


@pytest.fixture
def claims_with_nulls():
    """
    Provides a claims DataFrame with NULL values for validation testing
    
    Returns:
        pd.DataFrame with missing values
    """
    return pd.DataFrame({
        'patient_id': [101, 102, None, 104, 105],
        'provider_id': [501, 502, 501, None, 502],
        'claim_amount': [1000.0, None, 1500.0, 5000.0, 2000.0],
        'diagnosis_code': ['I10', 'E11', 'J45', 'I50', None],
    })


# ==================== FIXTURES: Network Data ====================

@pytest.fixture
def sample_network():
    """
    Provides a sample NetworkX graph for testing
    
    Returns:
        nx.Graph with sample patient-provider connections
    """
    G = nx.Graph()
    
    # Add nodes
    G.add_node("Patient_101", node_type='patient')
    G.add_node("Patient_102", node_type='patient')
    G.add_node("Provider_501", node_type='provider')
    G.add_node("Provider_502", node_type='provider')
    
    # Add edges
    G.add_edge("Patient_101", "Provider_501", claim_amount=1000)
    G.add_edge("Patient_101", "Provider_502", claim_amount=1500)
    G.add_edge("Patient_102", "Provider_501", claim_amount=2500)
    G.add_edge("Patient_102", "Provider_502", claim_amount=2000)
    
    return G


@pytest.fixture
def dense_network():
    """
    Provides a dense network with multiple cliques for testing
    
    Returns:
        nx.Graph with suspicious cliques
    """
    G = nx.Graph()
    
    # Create a clique (patients connected to same providers)
    patients = [f"Patient_{i}" for i in range(101, 106)]
    providers = [f"Provider_{i}" for i in range(501, 503)]
    
    for p in patients:
        G.add_node(p, node_type='patient')
    for pr in providers:
        G.add_node(pr, node_type='provider')
    
    # Create clique-like structure
    for p in patients[:3]:
        for pr in providers:
            G.add_edge(p, pr, claim_amount=1000)
    
    return G


# ==================== FIXTURES: Anomaly Data ====================

@pytest.fixture
def anomaly_results():
    """
    Provides a DataFrame with anomaly detection results
    
    Returns:
        pd.DataFrame with anomaly flags and scores
    """
    return pd.DataFrame({
        'patient_id': [101, 102, 103, 104, 105],
        'provider_id': [501, 502, 501, 503, 502],
        'claim_amount': [1000.0, 2500.0, 1500.0, 5000.0, 2000.0],
        'is_anomaly': [False, True, False, True, False],
        'anomaly_score': [0.2, 0.8, 0.3, 0.95, 0.4],
    })


# ==================== FIXTURES: Environment ====================

@pytest.fixture
def mock_openai_key(monkeypatch):
    """
    Mocks the OpenAI API key for testing
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test-key-12345')


@pytest.fixture
def temp_csv(tmp_path, sample_claims_df):
    """
    Creates a temporary CSV file for testing
    
    Args:
        tmp_path: Pytest temporary directory fixture
        sample_claims_df: Sample data fixture
    
    Returns:
        str: Path to temporary CSV file
    """
    csv_path = tmp_path / "test_claims.csv"
    sample_claims_df.to_csv(csv_path, index=False)
    return str(csv_path)


# ==================== PYTEST HOOKS ====================

def pytest_configure(config):
    """
    Pytest configuration hook - runs before test collection
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )


def pytest_collection_modifyitems(config, items):
    """
    Pytest hook to modify collected test items
    
    Automatically marks tests based on name patterns
    """
    for item in items:
        # Mark slow tests
        if "test_load" in item.nodeid or "test_large" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.nodeid or "api" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)


# ==================== TEST UTILITIES ====================

class MockStreamlit:
    """Mock Streamlit module for testing"""
    
    class Secrets(dict):
        def __init__(self):
            super().__init__()
            self['OPENAI_API_KEY'] = 'sk-test-key'
    
    secrets = Secrets()
    
    @staticmethod
    def cache_data(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def error(msg):
        pass
    
    @staticmethod
    def warning(msg):
        pass
    
    @staticmethod
    def info(msg):
        pass
    
    @staticmethod
    def write(msg):
        pass


@pytest.fixture
def mock_streamlit(monkeypatch):
    """
    Mocks Streamlit module for testing
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    import sys
    sys.modules['streamlit'] = MockStreamlit()
    yield MockStreamlit
    del sys.modules['streamlit']


# ==================== PYTEST FIXTURES: Performance ====================

@pytest.fixture
def benchmark_timer():
    """
    Provides a simple timer for benchmarking tests
    
    Yields:
        function: Timer context manager
    """
    import time
    from contextlib import contextmanager
    
    @contextmanager
    def timer():
        start = time.time()
        yield
        elapsed = time.time() - start
        print(f"\n⏱️ Elapsed time: {elapsed:.4f}s")
    
    return timer


# ==================== CLEANUP ====================

@pytest.fixture(autouse=True)
def cleanup_cache():
    """
    Cleans up any caches after each test
    """
    yield
    # Cleanup code here if needed
    pass

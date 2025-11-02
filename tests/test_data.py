"""
Unit tests for utils/data.py module

Tests data loading, validation, filtering, and statistical calculations
"""

import pytest
import pandas as pd
import numpy as np
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data import (
    sanitize_claims_data,
    filter_claims_by_parameters,
    get_statistics
)


class TestDataSanitization:
    """Tests for data sanitization and validation"""
    
    def test_sanitize_removes_duplicates(self, sample_claims_df):
        """Test that sanitize_claims_data removes duplicate rows"""
        df_with_dupes = pd.concat([sample_claims_df, sample_claims_df.iloc[0:2]])
        result = sanitize_claims_data(df_with_dupes)
        assert len(result) == len(sample_claims_df)
    
    def test_sanitize_keeps_valid_data(self, sample_claims_df):
        """Test that valid data is preserved after sanitization"""
        result = sanitize_claims_data(sample_claims_df.copy())
        assert len(result) == len(sample_claims_df)
        assert set(result.columns) == set(sample_claims_df.columns)
    
    def test_sanitize_handles_null_values(self, claims_with_nulls):
        """Test that null values are handled correctly"""
        result = sanitize_claims_data(claims_with_nulls)
        # Should remove rows with nulls in CRITICAL columns (patient_id, provider_id)
        # But diagnosis_code can be None (filled with 'UNKNOWN') and that's ok
        assert result['patient_id'].notna().all()
        assert result['provider_id'].notna().all()
    
    def test_sanitize_removes_negative_amounts(self, sample_claims_df):
        """Test that negative claim amounts are removed"""
        df = sample_claims_df.copy()
        df.loc[0, 'claim_amount'] = -1000
        result = sanitize_claims_data(df)
        assert (result['claim_amount'] > 0).all()
    
    def test_sanitize_preserves_data_types(self, sample_claims_df):
        """Test that data types are preserved/corrected"""
        result = sanitize_claims_data(sample_claims_df.copy())
        assert result['patient_id'].dtype in [np.int64, np.int32, int]
        assert result['provider_id'].dtype in [np.int64, np.int32, int]
        assert result['claim_amount'].dtype in [np.float64, np.float32, float]


class TestDataFiltering:
    """Tests for data filtering operations"""
    
    def test_filter_by_amount_min(self, sample_claims_df):
        """Test filtering by minimum amount"""
        result = filter_claims_by_parameters(sample_claims_df, min_amount=1500)
        assert (result['claim_amount'] >= 1500).all()
    
    def test_filter_by_amount_max(self, sample_claims_df):
        """Test filtering by maximum amount"""
        result = filter_claims_by_parameters(sample_claims_df, max_amount=2500)
        assert (result['claim_amount'] <= 2500).all()
    
    def test_filter_by_amount_range(self, sample_claims_df):
        """Test filtering by amount range"""
        result = filter_claims_by_parameters(
            sample_claims_df,
            min_amount=1000,
            max_amount=2500
        )
        assert (result['claim_amount'] >= 1000).all()
        assert (result['claim_amount'] <= 2500).all()
    
    def test_filter_by_patient_ids(self, sample_claims_df):
        """Test filtering by patient IDs"""
        patient_ids = [101, 103]
        result = filter_claims_by_parameters(sample_claims_df, patient_ids=patient_ids)
        assert set(result['patient_id'].unique()) == set(patient_ids)
    
    def test_filter_by_provider_ids(self, sample_claims_df):
        """Test filtering by provider IDs"""
        provider_ids = [501, 502]
        result = filter_claims_by_parameters(sample_claims_df, provider_ids=provider_ids)
        assert set(result['provider_id'].unique()) == set(provider_ids)
    
    def test_filter_combined(self, sample_claims_df):
        """Test combined filtering"""
        result = filter_claims_by_parameters(
            sample_claims_df,
            min_amount=1000,
            max_amount=3000,
            provider_ids=[501]
        )
        assert (result['claim_amount'] >= 1000).all()
        assert (result['claim_amount'] <= 3000).all()
        assert (result['provider_id'] == 501).all()
    
    def test_filter_no_parameters(self, sample_claims_df):
        """Test that filtering with no parameters returns all data"""
        result = filter_claims_by_parameters(sample_claims_df)
        assert len(result) == len(sample_claims_df)
    
    def test_filter_empty_result(self, sample_claims_df):
        """Test filtering that returns empty result"""
        result = filter_claims_by_parameters(sample_claims_df, min_amount=10000)
        assert len(result) == 0


class TestStatistics:
    """Tests for statistical calculations"""
    
    def test_get_statistics_complete(self, sample_claims_df):
        """Test that all statistics are calculated"""
        stats = get_statistics(sample_claims_df)
        assert 'total_claims' in stats
        assert 'total_amount' in stats
        assert 'avg_claim' in stats
        assert 'median_claim' in stats
        assert 'min_claim' in stats
        assert 'max_claim' in stats
        assert 'unique_patients' in stats
        assert 'unique_providers' in stats
    
    def test_get_statistics_values(self, sample_claims_df):
        """Test that statistics have correct values"""
        stats = get_statistics(sample_claims_df)
        assert stats['total_claims'] == 5
        assert stats['total_amount'] == 12000.0
        assert stats['avg_claim'] == 2400.0
        assert stats['unique_patients'] == 5
        assert stats['unique_providers'] == 3
    
    def test_get_statistics_empty_df(self, empty_claims_df):
        """Test statistics on empty DataFrame"""
        stats = get_statistics(empty_claims_df)
        assert stats == {}
    
    def test_statistics_with_large_dataset(self, large_claims_df):
        """Test statistics with larger dataset"""
        stats = get_statistics(large_claims_df)
        assert stats['total_claims'] == 1000
        assert stats['total_amount'] > 0
        assert stats['avg_claim'] > 0


class TestDataEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_empty_dataframe(self, empty_claims_df):
        """Test handling of empty DataFrame"""
        result = filter_claims_by_parameters(empty_claims_df)
        assert len(result) == 0
    
    def test_single_row_dataframe(self, sample_claims_df):
        """Test handling of single-row DataFrame"""
        single_row = sample_claims_df.iloc[0:1].copy()
        result = sanitize_claims_data(single_row)
        assert len(result) == 1
    
    def test_all_nulls_column(self):
        """Test handling of column with all nulls"""
        df = pd.DataFrame({
            'patient_id': [101, 102, 103],
            'provider_id': [501, 502, 503],
            'claim_amount': [None, None, None],
            'diagnosis_code': ['I10', 'E11', 'J45'],
        })
        result = sanitize_claims_data(df)
        # Now we keep rows with NULL claim_amount (filled as 0)
        # Only rows are removed if patient_id or provider_id are NULL
        assert len(result) == 3  # All rows kept (nulls filled as 0)
        assert (result['claim_amount'] >= 0).all()
    
    def test_zero_claim_amounts(self):
        """Test handling of zero claim amounts"""
        df = pd.DataFrame({
            'patient_id': [101, 102],
            'provider_id': [501, 502],
            'claim_amount': [0.0, 100.0],
            'diagnosis_code': ['I10', 'E11'],
        })
        result = sanitize_claims_data(df)
        # Now we KEEP zero amounts (they are valid claims)
        assert len(result) == 2  # Both rows kept
        assert (result['claim_amount'] >= 0).all()  # All amounts >= 0


class TestDataIntegration:
    """Integration tests for data operations"""
    
    def test_sanitize_then_filter(self, claims_with_nulls):
        """Test chaining sanitization and filtering"""
        sanitized = sanitize_claims_data(claims_with_nulls)
        filtered = filter_claims_by_parameters(sanitized, min_amount=1000)
        assert len(filtered) > 0
        assert (filtered['claim_amount'] >= 1000).all()
    
    def test_complete_workflow(self, sample_claims_df):
        """Test complete data processing workflow"""
        # Sanitize
        clean = sanitize_claims_data(sample_claims_df.copy())
        assert len(clean) == len(sample_claims_df)
        
        # Filter
        filtered = filter_claims_by_parameters(clean, min_amount=1500)
        assert (filtered['claim_amount'] >= 1500).all()
        
        # Statistics
        stats = get_statistics(filtered)
        assert stats['total_claims'] == len(filtered)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

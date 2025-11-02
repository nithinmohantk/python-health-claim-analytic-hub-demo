"""
Unit tests for utils/anomaly.py module

Tests anomaly detection methods, scoring, and analysis
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.anomaly import (
    detect_anomalies_threshold,
    detect_anomalies_statistical,
    detect_anomalies_isolation_forest,
    combine_anomaly_scores,
    get_top_anomalies,
    get_anomaly_summary
)


class TestThresholdDetection:
    """Tests for threshold-based anomaly detection"""
    
    def test_threshold_fixed_value(self, sample_claims_df):
        """Test threshold detection with fixed threshold"""
        result = detect_anomalies_threshold(sample_claims_df, threshold=2000)
        
        assert 'is_anomaly' in result.columns
        assert 'anomaly_score' in result.columns
        assert result[result['is_anomaly']]['claim_amount'].min() > 2000
    
    def test_threshold_percentile(self, sample_claims_df):
        """Test threshold detection with percentile"""
        result = detect_anomalies_threshold(sample_claims_df, percentile=75)
        
        assert 'is_anomaly' in result.columns
        assert result['is_anomaly'].any()  # Should have some anomalies
    
    def test_threshold_returns_df(self, sample_claims_df):
        """Test that threshold detection returns DataFrame"""
        result = detect_anomalies_threshold(sample_claims_df, threshold=1000)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_claims_df)
    
    def test_threshold_anomaly_scores_valid(self, sample_claims_df):
        """Test that anomaly scores are valid"""
        result = detect_anomalies_threshold(sample_claims_df, threshold=1500)
        assert (result['anomaly_score'] >= 0).all()


class TestStatisticalDetection:
    """Tests for statistical (Z-score) anomaly detection"""
    
    def test_statistical_z_score(self, sample_claims_df):
        """Test Z-score based detection"""
        result = detect_anomalies_statistical(sample_claims_df, z_threshold=2.0)
        
        assert 'is_anomaly' in result.columns
        assert 'z_score' in result.columns
        assert 'anomaly_score' in result.columns
    
    def test_statistical_returns_df(self, sample_claims_df):
        """Test that statistical detection returns DataFrame"""
        result = detect_anomalies_statistical(sample_claims_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_claims_df)
    
    def test_statistical_with_large_z_threshold(self, large_claims_df):
        """Test with high Z-score threshold"""
        result = detect_anomalies_statistical(large_claims_df, z_threshold=5.0)
        # Few or no anomalies with high threshold
        assert result['is_anomaly'].sum() <= len(large_claims_df) * 0.1
    
    def test_statistical_with_low_z_threshold(self, sample_claims_df):
        """Test with low Z-score threshold"""
        result = detect_anomalies_statistical(sample_claims_df, z_threshold=1.0)
        # More anomalies with low threshold
        assert result['is_anomaly'].any()


class TestIsolationForest:
    """Tests for Isolation Forest anomaly detection"""
    
    def test_isolation_forest_basic(self, sample_claims_df):
        """Test basic Isolation Forest detection"""
        result = detect_anomalies_isolation_forest(sample_claims_df, contamination=0.2)
        
        assert 'is_anomaly' in result.columns
        assert 'anomaly_score' in result.columns
    
    def test_isolation_forest_returns_df(self, sample_claims_df):
        """Test that Isolation Forest returns DataFrame"""
        result = detect_anomalies_isolation_forest(sample_claims_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_claims_df)
    
    def test_isolation_forest_contamination_rate(self, large_claims_df):
        """Test that contamination rate is respected"""
        contamination = 0.1
        result = detect_anomalies_isolation_forest(large_claims_df, contamination=contamination)
        
        actual_rate = result['is_anomaly'].sum() / len(result)
        # Allow some tolerance due to randomness
        assert 0 <= actual_rate <= contamination + 0.05
    
    def test_isolation_forest_with_single_feature(self, sample_claims_df):
        """Test with single feature"""
        result = detect_anomalies_isolation_forest(
            sample_claims_df,
            features=['claim_amount']
        )
        assert 'is_anomaly' in result.columns


class TestCombineScores:
    """Tests for combining multiple anomaly scores"""
    
    def test_combine_two_methods(self, sample_claims_df):
        """Test combining two anomaly detection methods"""
        threshold_result = detect_anomalies_threshold(sample_claims_df, threshold=2000)
        statistical_result = detect_anomalies_statistical(sample_claims_df)
        
        combined = combine_anomaly_scores(
            statistical_result,
            ['anomaly_score', 'is_anomaly'],
            weights=[0.6, 0.4]
        )
        
        assert 'combined_anomaly_score' in combined.columns
    
    def test_combine_equal_weights(self, anomaly_results):
        """Test combining with equal weights"""
        result = combine_anomaly_scores(
            anomaly_results,
            ['anomaly_score'],
            weights=[1.0]
        )
        
        assert result['combined_anomaly_score'].max() <= 1.0
    
    def test_combine_normalizes_weights(self, sample_claims_df):
        """Test that weights are normalized"""
        statistical_result = detect_anomalies_statistical(sample_claims_df)
        
        result1 = combine_anomaly_scores(
            statistical_result.copy(),
            ['anomaly_score'],
            weights=[1.0]
        )
        result2 = combine_anomaly_scores(
            statistical_result.copy(),
            ['anomaly_score'],
            weights=[2.0]
        )
        
        # Should be equal when weights are proportionally the same
        assert np.allclose(result1['combined_anomaly_score'], result2['combined_anomaly_score'])


class TestAnomalyRanking:
    """Tests for getting top anomalies"""
    
    def test_get_top_anomalies(self, anomaly_results):
        """Test getting top N anomalies"""
        result = get_top_anomalies(anomaly_results, n=2)
        
        assert len(result) == 2
        assert (result['anomaly_score'].iloc[0] >= result['anomaly_score'].iloc[1])
    
    def test_get_top_more_than_available(self, anomaly_results):
        """Test requesting more anomalies than available"""
        result = get_top_anomalies(anomaly_results, n=100)
        
        assert len(result) == len(anomaly_results)
    
    def test_get_top_maintains_order(self, anomaly_results):
        """Test that top anomalies are properly ordered"""
        result = get_top_anomalies(anomaly_results, n=5)
        
        # Check descending order
        scores = result['anomaly_score'].tolist()
        assert scores == sorted(scores, reverse=True)


class TestAnomalySummary:
    """Tests for anomaly summary statistics"""
    
    def test_anomaly_summary_keys(self, anomaly_results):
        """Test that summary has all required keys"""
        summary = get_anomaly_summary(anomaly_results)
        
        assert 'total_claims' in summary
        assert 'anomalies_detected' in summary
        assert 'anomaly_percentage' in summary
        assert 'normal_claims' in summary
    
    def test_anomaly_summary_values(self, anomaly_results):
        """Test that summary values are correct"""
        summary = get_anomaly_summary(anomaly_results)
        
        assert summary['total_claims'] == 5
        assert summary['anomalies_detected'] == 2
        assert 0 <= summary['anomaly_percentage'] <= 100
        assert summary['normal_claims'] == 3
    
    def test_anomaly_summary_empty_df(self, empty_claims_df):
        """Test summary on empty DataFrame"""
        summary = get_anomaly_summary(empty_claims_df)
        assert summary == {}


class TestAnomalyEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_all_anomalies(self):
        """Test when all data points are anomalies"""
        df = pd.DataFrame({
            'patient_id': [101, 102],
            'provider_id': [501, 502],
            'claim_amount': [10000, 15000],
            'diagnosis_code': ['I10', 'E11'],
        })
        
        result = detect_anomalies_threshold(df, threshold=1000)
        assert result['is_anomaly'].all()
    
    def test_no_anomalies(self):
        """Test when no data points are anomalies"""
        df = pd.DataFrame({
            'patient_id': [101, 102],
            'provider_id': [501, 502],
            'claim_amount': [100, 150],
            'diagnosis_code': ['I10', 'E11'],
        })
        
        result = detect_anomalies_threshold(df, threshold=10000)
        assert not result['is_anomaly'].any()
    
    def test_single_row_dataframe(self, sample_claims_df):
        """Test anomaly detection on single row"""
        single_row = sample_claims_df.iloc[0:1].copy()
        result = detect_anomalies_statistical(single_row)
        
        # Single row might not have meaningful z-scores
        assert len(result) == 1


class TestAnomalyIntegration:
    """Integration tests for anomaly detection"""
    
    def test_multiple_methods_workflow(self, sample_claims_df):
        """Test using multiple detection methods"""
        threshold = detect_anomalies_threshold(sample_claims_df, threshold=2000)
        statistical = detect_anomalies_statistical(sample_claims_df)
        forest = detect_anomalies_isolation_forest(sample_claims_df)
        
        # All should return DataFrames of same length
        assert len(threshold) == len(statistical) == len(forest) == len(sample_claims_df)
    
    def test_detection_ranking_workflow(self, sample_claims_df):
        """Test detecting then ranking anomalies"""
        result = detect_anomalies_threshold(sample_claims_df, threshold=1500)
        anomalies = result[result['is_anomaly']]
        top = get_top_anomalies(anomalies, n=3)
        
        assert len(top) <= 3
        assert all(top['is_anomaly'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Anomaly detection module for HealthClaim Analytics Hub
Implements multiple anomaly detection methods for fraud detection
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
import streamlit as st


def detect_anomalies_threshold(
    df: pd.DataFrame,
    column: str = 'claim_amount',
    threshold: float = None,
    percentile: int = None
) -> pd.DataFrame:
    """
    Detect anomalies using simple threshold-based approach.
    
    Args:
        df: Claims DataFrame
        column: Column to analyze for anomalies
        threshold: Fixed threshold value
        percentile: Percentile-based threshold (e.g., 95 for 95th percentile)
        
    Returns:
        DataFrame with anomaly flag and anomaly score
    """
    result = df.copy()
    
    if threshold is not None:
        result['anomaly_score'] = result[column] / threshold
        result['is_anomaly'] = result[column] > threshold
    elif percentile is not None:
        threshold = result[column].quantile(percentile / 100)
        result['anomaly_score'] = result[column] / threshold
        result['is_anomaly'] = result[column] > threshold
    else:
        result['anomaly_score'] = 0
        result['is_anomaly'] = False
    
    return result


def detect_anomalies_statistical(
    df: pd.DataFrame,
    column: str = 'claim_amount',
    z_threshold: float = 3.0
) -> pd.DataFrame:
    """
    Detect anomalies using statistical z-score method.
    
    Args:
        df: Claims DataFrame
        column: Column to analyze
        z_threshold: Z-score threshold (standard deviations from mean)
        
    Returns:
        DataFrame with anomaly flag and z-scores
    """
    result = df.copy()
    
    mean = result[column].mean()
    std = result[column].std()
    
    result['z_score'] = np.abs((result[column] - mean) / std)
    result['is_anomaly'] = result['z_score'] > z_threshold
    result['anomaly_score'] = result['z_score']
    
    return result


@st.cache_data
def detect_anomalies_isolation_forest(
    df: pd.DataFrame,
    features: List[str] = None,
    contamination: float = 0.05,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Detect anomalies using Isolation Forest algorithm.
    More sophisticated ML-based approach for complex patterns.
    
    Args:
        df: Claims DataFrame
        features: List of columns to use for anomaly detection
        contamination: Expected proportion of outliers (0.0 to 0.5)
        random_state: Random seed for reproducibility
        
    Returns:
        DataFrame with anomaly predictions and scores
    """
    result = df.copy()
    
    if features is None:
        features = ['claim_amount']
    
    # Ensure features exist and are numeric
    available_features = [f for f in features if f in df.columns]
    if not available_features:
        result['is_anomaly'] = False
        result['anomaly_score'] = 0
        return result
    
    # Prepare data
    X = result[available_features].copy()
    X = X.fillna(X.mean())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=100
    )
    
    # Predict anomalies (-1 = anomaly, 1 = normal)
    predictions = iso_forest.fit_predict(X_scaled)
    scores = iso_forest.score_samples(X_scaled)
    
    result['is_anomaly'] = predictions == -1
    result['anomaly_score'] = -scores  # Negate so higher = more anomalous
    
    return result


def detect_frequency_anomalies(
    df: pd.DataFrame,
    entity_col: str = 'provider_id',
    window: str = 'D',
    threshold_percentile: int = 90
) -> pd.DataFrame:
    """
    Detect anomalies based on claim frequency patterns.
    
    Args:
        df: Claims DataFrame with date column
        entity_col: Column to group by (provider_id, patient_id, etc.)
        window: Time window for frequency ('D'=day, 'W'=week, 'M'=month)
        threshold_percentile: Percentile threshold for flagging as anomaly
        
    Returns:
        DataFrame with frequency anomaly indicators
    """
    result = df.copy()
    
    if 'date' not in result.columns:
        result['frequency_anomaly'] = False
        return result
    
    # Group by entity and date window, count occurrences
    result['date'] = pd.to_datetime(result['date'])
    result['date_window'] = result['date'].dt.to_period(window)
    
    frequency = result.groupby([entity_col, 'date_window']).size().reset_index(name='claim_count')
    
    # Calculate threshold
    threshold = frequency['claim_count'].quantile(threshold_percentile / 100)
    
    # Merge back to original
    freq_anomaly = frequency[frequency['claim_count'] > threshold]
    result['frequency_anomaly'] = result.apply(
        lambda row: (row[entity_col], row['date_window']) in 
                    zip(freq_anomaly[entity_col], freq_anomaly['date_window']),
        axis=1
    )
    
    return result


def combine_anomaly_scores(
    df: pd.DataFrame,
    anomaly_columns: List[str],
    weights: List[float] = None
) -> pd.DataFrame:
    """
    Combine multiple anomaly detection methods into a single score.
    
    Args:
        df: DataFrame with multiple anomaly score columns
        anomaly_columns: List of anomaly score column names
        weights: Optional weights for each column
        
    Returns:
        DataFrame with combined anomaly score
    """
    result = df.copy()
    
    if weights is None:
        weights = [1.0] * len(anomaly_columns)
    
    # Normalize weights
    weights = [w / sum(weights) for w in weights]
    
    # Calculate weighted average
    result['combined_anomaly_score'] = 0.0
    for col, weight in zip(anomaly_columns, weights):
        if col in result.columns:
            # Normalize column to 0-1 range
            col_min = result[col].min()
            col_max = result[col].max()
            if col_max > col_min:
                normalized = (result[col] - col_min) / (col_max - col_min)
            else:
                normalized = 0
            result['combined_anomaly_score'] += normalized * weight
    
    return result


def get_top_anomalies(
    df: pd.DataFrame,
    anomaly_score_col: str = 'anomaly_score',
    n: int = 10
) -> pd.DataFrame:
    """
    Get top N anomalies sorted by anomaly score.
    
    Args:
        df: DataFrame with anomaly scores
        anomaly_score_col: Name of anomaly score column
        n: Number of top anomalies to return
        
    Returns:
        Top N anomalies sorted by score
    """
    if anomaly_score_col not in df.columns:
        return df.head(n)
    
    return df.nlargest(n, anomaly_score_col)


def get_anomaly_summary(
    df: pd.DataFrame,
    anomaly_col: str = 'is_anomaly'
) -> dict:
    """
    Get summary statistics about detected anomalies.
    
    Args:
        df: DataFrame with anomaly flags
        anomaly_col: Name of anomaly column
        
    Returns:
        Dictionary with anomaly statistics
    """
    if anomaly_col not in df.columns:
        return {}
    
    total = len(df)
    anomalies = df[df[anomaly_col]].shape[0]
    
    return {
        'total_claims': total,
        'anomalies_detected': anomalies,
        'anomaly_percentage': (anomalies / total * 100) if total > 0 else 0,
        'normal_claims': total - anomalies,
        'avg_amount_anomaly': df[df[anomaly_col]]['claim_amount'].mean() if anomalies > 0 else 0,
        'avg_amount_normal': df[~df[anomaly_col]]['claim_amount'].mean() if (total - anomalies) > 0 else 0,
    }

"""
Data loading and processing module for HealthClaim Analytics Hub
Handles loading patient claims data and preprocessing
"""

import pandas as pd
import streamlit as st
from typing import Optional


@st.cache_data(ttl=3600)
def load_claims_data(url: Optional[str] = None) -> pd.DataFrame:
    """
    Load patient claims data from GitHub or local source.
    
    Args:
        url: URL to claims CSV. Defaults to neural-nexus repo.
        
    Returns:
        DataFrame with columns: patient_id, provider_id, claim_amount, 
        diagnosis_code, date, procedure_code
    """
    if url is None:
        url = "https://raw.githubusercontent.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis/main/data/claims_sample.csv"
    
    try:
        df = pd.read_csv(url)
        
        # Validate required columns
        required_cols = ['patient_id', 'provider_id', 'claim_amount', 'diagnosis_code']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return pd.DataFrame()
        
        # Data validation and sanitization
        df = sanitize_claims_data(df)
        return df
        
    except Exception as e:
        st.error(f"Error loading claims data: {str(e)}")
        return pd.DataFrame()


def sanitize_claims_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and sanitize claims data for security and quality.
    
    Args:
        df: Raw claims DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Ensure numeric fields are properly typed
    numeric_cols = ['patient_id', 'provider_id', 'claim_amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with NaN in critical columns (including diagnosis_code)
    critical_cols = ['patient_id', 'provider_id', 'claim_amount', 'diagnosis_code']
    cols_to_check = [col for col in critical_cols if col in df.columns]
    df = df.dropna(subset=cols_to_check)
    
    # Ensure claim amounts are positive
    df = df[df['claim_amount'] > 0]
    
    # Convert date columns if present
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    return df


def filter_claims_by_parameters(
    df: pd.DataFrame,
    patient_ids: Optional[list] = None,
    provider_ids: Optional[list] = None,
    date_range: Optional[tuple] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> pd.DataFrame:
    """
    Filter claims data based on user-specified parameters.
    
    Args:
        df: Original claims DataFrame
        patient_ids: List of patient IDs to include
        provider_ids: List of provider IDs to include
        date_range: Tuple of (start_date, end_date)
        min_amount: Minimum claim amount filter
        max_amount: Maximum claim amount filter
        
    Returns:
        Filtered DataFrame
    """
    result = df.copy()
    
    if patient_ids:
        result = result[result['patient_id'].isin(patient_ids)]
    
    if provider_ids:
        result = result[result['provider_id'].isin(provider_ids)]
    
    if date_range and 'date' in result.columns:
        start_date, end_date = date_range
        result = result[(result['date'] >= start_date) & (result['date'] <= end_date)]
    
    if min_amount is not None:
        result = result[result['claim_amount'] >= min_amount]
    
    if max_amount is not None:
        result = result[result['claim_amount'] <= max_amount]
    
    return result


def get_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for claims data.
    
    Args:
        df: Claims DataFrame
        
    Returns:
        Dictionary with statistics
    """
    if df.empty:
        return {}
    
    return {
        'total_claims': len(df),
        'total_amount': df['claim_amount'].sum(),
        'avg_claim': df['claim_amount'].mean(),
        'median_claim': df['claim_amount'].median(),
        'min_claim': df['claim_amount'].min(),
        'max_claim': df['claim_amount'].max(),
        'std_dev': df['claim_amount'].std(),
        'unique_patients': df['patient_id'].nunique(),
        'unique_providers': df['provider_id'].nunique(),
    }

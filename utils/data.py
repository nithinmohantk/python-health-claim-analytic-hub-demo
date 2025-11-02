"""
Data loading and processing module for HealthClaim Analytics Hub
Handles loading patient claims data and preprocessing
"""

import pandas as pd
import streamlit as st
from typing import Optional
import numpy as np
from datetime import datetime, timedelta
import requests
from io import StringIO


def generate_sample_claims_data(num_records: int = 1000) -> pd.DataFrame:
    """
    Generate sample healthcare claims data for demonstration.
    Useful as fallback when external data sources are unavailable.
    
    Args:
        num_records: Number of sample claims to generate
        
    Returns:
        DataFrame with sample claims data
    """
    np.random.seed(42)
    
    # Generate realistic data
    patient_ids = np.random.randint(1000, 5000, num_records)
    provider_ids = np.random.randint(100, 500, num_records)
    
    # Realistic claim amounts ($100 - $10,000)
    claim_amounts = np.random.gamma(shape=2, scale=1000, size=num_records)
    claim_amounts = np.clip(claim_amounts, 100, 10000)
    
    # Diagnosis codes (simplified)
    diagnosis_codes = [f"ICD-{np.random.randint(1000, 9999)}" for _ in range(num_records)]
    
    # Procedure codes
    procedure_codes = [f"CPT-{np.random.randint(10000, 99999)}" for _ in range(num_records)]
    
    # Dates (last 365 days)
    dates = [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(num_records)]
    
    df = pd.DataFrame({
        'patient_id': patient_ids,
        'provider_id': provider_ids,
        'claim_amount': claim_amounts,
        'diagnosis_code': diagnosis_codes,
        'procedure_code': procedure_codes,
        'date': dates
    })
    
    return df


@st.cache_data(ttl=3600)
def load_claims_data(url: Optional[str] = None, _cache_buster: int = 1) -> pd.DataFrame:
    """
    Load patient claims data from GitHub or local source.
    Handles both single CSV and merged claims+transactions data.
    Falls back to generated sample data if URL is unavailable.
    
    Args:
        url: URL to claims CSV. Defaults to neural-nexus repo.
        _cache_buster: Internal parameter to invalidate cache (not meant for user use)
        
    Returns:
        DataFrame with columns: patient_id, provider_id, claim_amount, 
        diagnosis_code, date, procedure_code
    """
    if url is None:
        # Try to load from the actual GitHub structure with merged data
        claims_url = "https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis/raw/main/data/sample_data/csv/galway/claims.csv"
        transactions_url = "https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis/raw/main/data/sample_data/csv/galway/claims_transactions.csv"
        return _load_and_merge_claims_data(claims_url, transactions_url)
    
    try:
        df = pd.read_csv(url)
        
        # Validate required columns
        required_cols = ['patient_id', 'provider_id', 'claim_amount', 'diagnosis_code']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            # If standard columns missing, assume it needs merging
            if 'PATIENTID' in df.columns or 'CLAIMID' in df.columns:
                # This is the GitHub format, try to merge with transactions
                st.info("Detected healthcare dataset format - loading and merging claims data...")
                claims_url = "https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis/raw/main/data/sample_data/csv/galway/claims.csv"
                transactions_url = "https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis/raw/main/data/sample_data/csv/galway/claims_transactions.csv"
                return _load_and_merge_claims_data(claims_url, transactions_url)
            else:
                st.error(f"Missing required columns: {missing_cols}")
                return pd.DataFrame()
        
        # Data validation and sanitization
        df = sanitize_claims_data(df)
        return df
        
    except Exception as e:
        # Fallback: Generate sample data
        st.warning(f"⚠️ Could not load from {url}\nUsing generated sample data instead.")
        df = generate_sample_claims_data(num_records=1000)
        df = sanitize_claims_data(df)
        return df


def _load_and_merge_claims_data(claims_url: str, transactions_url: str) -> pd.DataFrame:
    """
    Load and merge claims and transactions data from GitHub.
    Maps healthcare dataset schema to our standardized columns.
    
    Args:
        claims_url: URL to claims CSV
        transactions_url: URL to transactions CSV
        
    Returns:
        Merged and mapped DataFrame
    """
    try:
        # Load both datasets using requests to bypass Git LFS
        st.write("🔍 Loading claims CSV from GitHub...")
        claims_response = requests.get(claims_url, timeout=30)
        claims_response.raise_for_status()
        claims_df = pd.read_csv(StringIO(claims_response.text))
        st.write(f"✅ Loaded claims: {claims_df.shape[0]} rows, {claims_df.shape[1]} cols")
        st.write(f"   Columns: {list(claims_df.columns)[:10]}...")
        
        # Load transactions CSV
        st.write("🔍 Loading transactions CSV from GitHub...")
        trans_response = requests.get(transactions_url, timeout=30)
        trans_response.raise_for_status()
        transactions_df = pd.read_csv(StringIO(trans_response.text))
        st.write(f"✅ Loaded transactions: {transactions_df.shape[0]} rows, {transactions_df.shape[1]} cols")
        st.write(f"   Columns: {list(transactions_df.columns)[:10]}...")
        
        # Rename transaction columns for clarity
        st.write("🔍 Renaming transaction columns...")
        rename_dict = {
            'ID': 'TRANSACTIONID',
            'APPOINTMENTID': 'TRANS_APPOINTMENTID'
        }
        # Only rename if they exist
        rename_dict = {k: v for k, v in rename_dict.items() if k in transactions_df.columns}
        transactions_df = transactions_df.rename(columns=rename_dict)
        st.write(f"✅ Renamed columns: {rename_dict}")
        
        # Convert date columns to datetime
        st.write("🔍 Converting date columns...")
        if 'SERVICEDATE' in claims_df.columns:
            claims_df['SERVICEDATE'] = pd.to_datetime(claims_df['SERVICEDATE'], errors='coerce')
        
        if 'FROMDATE' in transactions_df.columns:
            transactions_df['FROMDATE'] = pd.to_datetime(transactions_df['FROMDATE'], errors='coerce')
        st.write("✅ Date conversion complete")
        
        # Merge claims and transactions on Id/CLAIMID
        st.write("🔍 Merging claims and transactions on Id/CLAIMID...")
        st.write(f"   Claims Id unique: {claims_df['Id'].nunique()}")
        st.write(f"   Transactions CLAIMID unique: {transactions_df['CLAIMID'].nunique()}")
        
        merged_df = pd.merge(
            claims_df,
            transactions_df,
            left_on='Id',
            right_on='CLAIMID',
            how='left',
            suffixes=('_claims', '_trans')  # Add suffixes to avoid conflicts
        )
        st.write(f"✅ Merged data: {merged_df.shape[0]} rows")
        st.write(f"   Merged columns: {list(merged_df.columns)[:15]}...")
        
        # Map to standardized columns
        st.write("🔍 Mapping to standardized schema...")
        st.write(f"   Available columns in merged data: {list(merged_df.columns)}")
        
        # Handle both PATIENTID and PATIENTID_claims/trans variants
        # After merge with suffixes, columns are: PATIENTID_claims, PATIENTID_trans
        patient_id_col = 'PATIENTID_claims' if 'PATIENTID_claims' in merged_df.columns else 'PATIENTID'
        provider_id_col = 'PROVIDERID_claims' if 'PROVIDERID_claims' in merged_df.columns else 'PROVIDERID'
        
        patient_id = merged_df[patient_id_col]
        provider_id = merged_df[provider_id_col]
        
        # Get diagnosis code from claims (use DIAGNOSIS1 as primary)
        if 'DIAGNOSIS1' in merged_df.columns:
            diagnosis_col = merged_df['DIAGNOSIS1']
        else:
            diagnosis_col = pd.Series(['UNKNOWN'] * len(merged_df), index=merged_df.index)
        
        st.write(f"   diagnosis_col: {diagnosis_col.notna().sum()} non-null, {diagnosis_col.isna().sum()} null")
        
        # Get amount from transactions (may be AMOUNT or None after merge)
        if 'AMOUNT' in merged_df.columns:
            claim_amount = merged_df['AMOUNT'].fillna(0)
        else:
            claim_amount = pd.Series([0]*len(merged_df), index=merged_df.index)
        
        st.write(f"   claim_amount: {(claim_amount > 0).sum()} positive, {(claim_amount <= 0).sum()} zero/negative")
        
        # Get procedure code
        if 'PROCEDURECODE' in merged_df.columns:
            procedure_code = merged_df['PROCEDURECODE'].fillna('UNKNOWN')
        else:
            procedure_code = pd.Series(['UNKNOWN']*len(merged_df), index=merged_df.index)
        
        # Get date - prefer SERVICEDATE from claims, fallback to FROMDATE from transactions
        if 'SERVICEDATE' in merged_df.columns:
            date_col = merged_df['SERVICEDATE']
        elif 'FROMDATE' in merged_df.columns:
            date_col = merged_df['FROMDATE']
        else:
            date_col = pd.Series([pd.NaT]*len(merged_df), index=merged_df.index)
        
        # Map columns to our standard schema
        # CRITICAL: Reset index to avoid alignment issues
        standardized_df = pd.DataFrame({
            'patient_id': patient_id.reset_index(drop=True).values,
            'provider_id': provider_id.reset_index(drop=True).values,
            'claim_amount': claim_amount.reset_index(drop=True).values,
            'diagnosis_code': diagnosis_col.astype(str).fillna('UNKNOWN').reset_index(drop=True).values,
            'procedure_code': procedure_code.reset_index(drop=True).values,
            'date': date_col.reset_index(drop=True).values
        })
        
        st.write(f"✅ Standardized schema: {standardized_df.shape}")
        st.write(f"   Columns: {list(standardized_df.columns)}")
        st.write(f"   Data types: {dict(standardized_df.dtypes)}")
        st.write(f"   Null values before sanitization:")
        st.write(f"     patient_id: {standardized_df['patient_id'].isna().sum()}")
        st.write(f"     provider_id: {standardized_df['provider_id'].isna().sum()}")
        st.write(f"     claim_amount: {standardized_df['claim_amount'].isna().sum()}")
        st.write(f"     diagnosis_code: {standardized_df['diagnosis_code'].isna().sum()}")
        st.write(f"     procedure_code: {standardized_df['procedure_code'].isna().sum()}")
        
        # CRITICAL DEBUG: Show first 5 rows of actual data
        st.write(f"   First 5 rows of standardized data:")
        for idx in range(min(5, len(standardized_df))):
            row = standardized_df.iloc[idx]
            st.write(f"     Row {idx}: patient_id={row['patient_id']} (type={type(row['patient_id']).__name__}), " +
                    f"provider_id={row['provider_id']} (type={type(row['provider_id']).__name__})")
        
        # Data validation and sanitization
        st.write("🔍 Sanitizing data...")
        standardized_df = sanitize_claims_data(standardized_df)
        st.write(f"✅ Final data: {standardized_df.shape[0]} rows after sanitization")
        
        return standardized_df
        
    except Exception as e:
        st.error(f"❌ Could not load and merge claims data: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        st.error(f"🔍 Full error trace:\n{error_trace}")
        st.warning("Using generated sample data instead.")
        print(f"\n\n⚠️  ERROR in load_claims_data: {str(e)}")
        print(f"Traceback:\n{error_trace}\n\n")
        df = generate_sample_claims_data(num_records=1000)
        df = sanitize_claims_data(df)
        return df


def sanitize_claims_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and sanitize claims data for security and quality.
    
    Args:
        df: Raw claims DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    initial_rows = len(df)
    st.write(f"   📊 Starting sanitization: {initial_rows} rows")
    st.write(f"   Columns present: {list(df.columns)}")
    
    # Check what we have BEFORE any transformation
    st.write(f"   Initial null counts:")
    for col in df.columns:
        st.write(f"     • {col}: {df[col].isna().sum()} nulls, dtype={df[col].dtype}")
    
    # CRITICAL: Show sample values BEFORE conversion
    st.write(f"   Sample values BEFORE conversion:")
    for col in ['patient_id', 'provider_id', 'claim_amount']:
        if col in df.columns:
            samples = df[col].head(5).tolist()
            types = [type(v).__name__ for v in samples]
            st.write(f"     • {col}: {samples} (types: {types})")
    
    # Remove duplicate rows
    df = df.drop_duplicates()
    after_dedup = len(df)
    st.write(f"   ✓ After drop_duplicates: {after_dedup} rows (removed {initial_rows - after_dedup})")
    
    # For numeric fields: only convert if they're not already numeric
    numeric_cols = ['patient_id', 'provider_id', 'claim_amount']
    for col in numeric_cols:
        if col in df.columns:
            before_dtype = df[col].dtype
            before_null = df[col].isna().sum()
            
            # CRITICAL: Don't try to convert UUIDs (strings) to numeric!
            # Check if column contains UUIDs or other non-numeric data
            if df[col].dtype == 'object':
                # Sample a value to check if it looks like a UUID
                sample_val = str(df[col].iloc[0]) if len(df) > 0 else ""
                is_uuid = len(sample_val) == 36 and sample_val.count('-') == 4
                
                if is_uuid:
                    st.write(f"   • {col}: UUID string format, keeping as-is (not converting to numeric)")
                    continue
            
            # Check if already numeric
            if df[col].dtype in ['int64', 'int32', 'float64', 'float32', 'int', 'float']:
                st.write(f"   • {col}: already numeric ({df[col].dtype}), {before_null} nulls")
            else:
                st.write(f"   • {col}: converting from {df[col].dtype} to numeric...")
                # Show what we're converting
                sample_vals = df[col].head(10).unique()
                st.write(f"     Sample values to convert: {sample_vals}")
                
                # CRITICAL: Try conversion carefully
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    after_null = df[col].isna().sum()
                    created_nulls = after_null - before_null
                    if created_nulls > 0:
                        st.error(f"     ⚠️  CONVERSION FAILED: Created {created_nulls} new NaNs!")
                        st.write(f"     This means {created_nulls} values couldn't be parsed as numbers")
                        # Show which values failed
                        sample_failed = df[df[col].isna()][col].head(5).tolist()
                        st.write(f"     Examples of values that failed: {sample_failed}")
                    else:
                        st.write(f"     ✓ Conversion successful: {after_null} nulls (was {before_null})")
                except Exception as conversion_error:
                    st.error(f"     ❌ CONVERSION ERROR: {str(conversion_error)}")
    
    after_numeric = len(df)
    st.write(f"   ✓ After numeric handling: {after_numeric} rows")
    st.write(f"   Null counts after numeric conversion:")
    for col in numeric_cols:
        if col in df.columns:
            st.write(f"     • {col}: {df[col].isna().sum()} nulls")
    
    # Drop rows with NaN in CRITICAL columns ONLY
    critical_cols = ['patient_id', 'provider_id']
    cols_to_check = [col for col in critical_cols if col in df.columns]
    
    if cols_to_check:
        # Show what we're about to drop
        null_mask = df[cols_to_check].isna().any(axis=1)
        rows_with_nulls = null_mask.sum()
        st.write(f"   ⚠️  Found {rows_with_nulls} rows with nulls in {cols_to_check}")
        
        if rows_with_nulls > 0:
            # Show a sample of rows that will be dropped
            sample_to_drop = df[null_mask].head(3)
            st.write(f"     Sample rows to be dropped:")
            for idx, row in sample_to_drop.iterrows():
                st.write(f"       Row {idx}: patient_id={row.get('patient_id')}, provider_id={row.get('provider_id')}")
        
        before = len(df)
        df = df.dropna(subset=cols_to_check)
        after = len(df)
        st.write(f"   ✓ After dropna: {after} rows (dropped {before - after})")
    
    # Handle claim_amount: fill NaN with 0, then keep only >= 0
    if 'claim_amount' in df.columns:
        before = len(df)
        null_count = df['claim_amount'].isna().sum()
        st.write(f"   • claim_amount: {null_count} nulls before fillna")
        df['claim_amount'] = df['claim_amount'].fillna(0)
        
        negative_count = (df['claim_amount'] < 0).sum()
        st.write(f"   • claim_amount: {negative_count} negative values")
        
        df = df[df['claim_amount'] >= 0].copy()
        after = len(df)
        st.write(f"   ✓ After claim_amount >= 0: {after} rows (dropped {before - after})")
    
    # Convert date columns if present
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    final_rows = len(df)
    retention_pct = 100 * final_rows / initial_rows if initial_rows > 0 else 0
    st.write(f"   ✅ Sanitization complete: {final_rows} rows ({retention_pct:.1f}% retained)")
    
    # Debug: if we lost everything, show sample of original data
    if final_rows == 0 and initial_rows > 0:
        st.error("⚠️ CRITICAL: All rows removed during sanitization!")
        st.write("🔍 DIAGNOSIS:")
        st.write("   This typically means:")
        st.write("   1. patient_id and provider_id couldn't be converted to numbers")
        st.write("   2. The data format is different than expected")
        st.write("   3. Column names don't match the merge output")
        st.write("")
        st.write("💡 SOLUTIONS:")
        st.write("   • Check that merge created PATIENTID_claims and PROVIDERID_claims columns")
        st.write("   • Verify numeric conversion didn't create NaNs (check 'Sample values' above)")
        st.write("   • If columns are strings like 'P123', they need stripping before conversion")
    
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

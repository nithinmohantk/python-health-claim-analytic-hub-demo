"""
GPT Integration module for HealthClaim Analytics Hub
Handles OpenAI API interactions and prompt generation
"""

import streamlit as st
import pandas as pd
from typing import Optional, List
import openai


def initialize_openai():
    """Initialize OpenAI API with credentials from Streamlit secrets."""
    if "OPENAI_API_KEY" not in st.secrets:
        st.error(
            "⚠️ Please add your OpenAI API key to Streamlit secrets as 'OPENAI_API_KEY'. "
            "See .streamlit/secrets.toml.example for setup instructions."
        )
        return False
    
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    return True


def generate_anomaly_explanation(
    claim_row: pd.Series,
    context: Optional[str] = None,
    model: str = "gpt-4",
    max_tokens: int = 250
) -> Optional[str]:
    """
    Generate natural language explanation for an anomalous claim using GPT.
    
    Args:
        claim_row: Pandas Series with claim data
        context: Additional context about the claim or dataset
        model: OpenAI model to use (gpt-4, gpt-3.5-turbo, etc.)
        max_tokens: Maximum tokens in response
        
    Returns:
        Explanation text or None if API fails
    """
    if not initialize_openai():
        return None
    
    # Build prompt with claim information
    prompt_lines = [
        "You are a healthcare fraud detection expert. Analyze this claim for potential fraud, waste, or abuse (FWA):",
        f"- Patient ID: {claim_row.get('patient_id', 'N/A')}",
        f"- Provider ID: {claim_row.get('provider_id', 'N/A')}",
        f"- Claim Amount: ${claim_row.get('claim_amount', 'N/A'):,.2f}",
        f"- Diagnosis Code: {claim_row.get('diagnosis_code', 'N/A')}",
    ]
    
    if 'procedure_code' in claim_row and pd.notna(claim_row['procedure_code']):
        prompt_lines.append(f"- Procedure Code: {claim_row['procedure_code']}")
    
    if 'date' in claim_row:
        prompt_lines.append(f"- Claim Date: {claim_row['date']}")
    
    if context:
        prompt_lines.append(f"\nAdditional Context: {context}")
    
    prompt_lines.append(
        "\nExplain if this claim looks suspicious based on healthcare fraud patterns. "
        "Provide specific reasons and recommend investigation priority."
    )
    
    prompt = "\n".join(prompt_lines)
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare fraud analyst providing concise, actionable insights."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=30
        )
        
        return response['choices'][0]['message']['content']
        
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "authentication" in error_str:
            st.error("❌ Authentication failed. Please check your OpenAI API key.")
        elif "rate" in error_str or "429" in error_str:
            st.warning("⚠️ Rate limit reached. Please try again in a moment.")
        else:
            st.error(f"❌ Error calling OpenAI API: {str(e)}")
        return None


def generate_network_insights(
    network_stats: dict,
    suspicious_clusters: dict,
    total_claims: int,
    model: str = "gpt-4"
) -> Optional[str]:
    """
    Generate insights about the patient-provider network using GPT.
    
    Args:
        network_stats: Network statistics dictionary
        suspicious_clusters: Suspicious cluster information
        total_claims: Total number of claims
        model: OpenAI model to use
        
    Returns:
        Network insights text or None if API fails
    """
    if not initialize_openai():
        return None
    
    # Safely format network stats (handle 'N/A' strings)
    avg_degree = network_stats.get('avg_degree', 'N/A')
    if isinstance(avg_degree, str):
        avg_degree_str = avg_degree
    else:
        avg_degree_str = f"{float(avg_degree):.2f}"
    
    density = network_stats.get('density', 'N/A')
    if isinstance(density, str):
        density_str = density
    else:
        density_str = f"{float(density):.3f}"
    
    prompt = f"""You are a healthcare fraud investigation expert. Analyze this network analysis summary:

Network Statistics:
- Total Nodes: {network_stats.get('num_nodes', 'N/A')} (patients and providers)
- Total Connections: {network_stats.get('num_edges', 'N/A')}
- Average Connections per Node: {avg_degree_str}
- Network Density: {density_str}
- Connected Components: {network_stats.get('num_connected_components', 'N/A')}
- Total Claims: {total_claims}

Suspicious Clusters:
- Cliques Identified: {suspicious_clusters.get('suspicious_cliques', 'N/A')}
- Total Cliques Found: {suspicious_clusters.get('total_cliques', 'N/A')}

Based on this network analysis, identify:
1. Key risk indicators and patterns that suggest potential fraud rings
2. Recommendations for investigative priority
3. Suggested next steps for deep-dive analysis

Be specific and actionable in your response."""
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare network fraud analyst specializing in identifying fraud rings."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400,
            timeout=30
        )
        
        return response['choices'][0]['message']['content']
        
    except Exception as e:
        st.error(f"Error generating network insights: {str(e)}")
        return None


def answer_claims_question(
    question: str,
    claims_summary: str,
    model: str = "gpt-4"
) -> Optional[str]:
    """
    Answer analyst questions about claims data using GPT.
    
    Args:
        question: User question about the claims data
        claims_summary: Summary of current claims data and filters
        model: OpenAI model to use
        
    Returns:
        Answer text or None if API fails
    """
    if not initialize_openai():
        return None
    
    prompt = f"""You are a healthcare claims data analyst. A fraud investigator has asked the following question:

Question: {question}

Current Data Context:
{claims_summary}

Provide a detailed, factual answer based on the data context. If the data is insufficient to answer, 
explain what additional information would be needed."""
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare claims analyst providing accurate, data-driven answers."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300,
            timeout=30
        )
        
        return response['choices'][0]['message']['content']
        
    except Exception as e:
        st.error(f"Error answering question: {str(e)}")
        return None


def validate_api_connection() -> bool:
    """
    Validate OpenAI API connection with a simple test call.
    
    Returns:
        True if connection successful, False otherwise
    """
    if not initialize_openai():
        return False
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'ready' in one word."}
            ],
            temperature=0.3,
            max_tokens=10,
            timeout=10
        )
        
        return response['choices'][0]['message']['content'].lower().strip() == 'ready'
        
    except Exception as e:
        st.error(f"API Connection Test Failed: {str(e)}")
        return False

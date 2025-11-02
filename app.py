"""
HealthClaim Analytics Hub - Main Application
A Streamlit web app for patient claims fraud analysis with GPT integration
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data import load_claims_data, sanitize_claims_data, filter_claims_by_parameters, get_statistics
from network import (
    build_patient_provider_network,
    create_network_visualization,
    get_network_statistics,
    detect_suspicious_clusters
)
from anomaly import (
    detect_anomalies_threshold,
    detect_anomalies_statistical,
    detect_anomalies_isolation_forest,
    get_top_anomalies,
    get_anomaly_summary,
    combine_anomaly_scores
)
from gpt import (
    initialize_openai,
    generate_anomaly_explanation,
    generate_network_insights,
    answer_claims_question,
    validate_api_connection
)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="HealthClaim Analytics Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .anomaly-high {
        background-color: #ffcccc;
        padding: 10px;
        border-radius: 5px;
    }
    .anomaly-medium {
        background-color: #fff4cc;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if 'claims_data' not in st.session_state:
    st.session_state.claims_data = None

if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

if 'anomalies' not in st.session_state:
    st.session_state.anomalies = None

if 'gpt_initialized' not in st.session_state:
    st.session_state.gpt_initialized = False

# ==================== MAIN HEADER ====================
st.title("🏥 HealthClaim Analytics Hub")
st.markdown("AI-Powered Patient Claims Fraud Detection & Network Analysis")

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Data loading section
    st.subheader("📊 Data Loading")
    
    with st.expander("Data Source Settings", expanded=False):
        data_source = st.radio(
            "Choose data source:",
            ["Default (GitHub)", "Upload CSV"],
            key="data_source"
        )
        
        custom_url = None
        if data_source == "Default (GitHub)":
            st.info("Loading claims data from neural-nexus repository...")
        else:
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    # Sanitize uploaded data to ensure proper formatting
                    df = sanitize_claims_data(df)
                    st.session_state.claims_data = df
                    st.success("✅ File uploaded successfully!")
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
    
    # Load data button
    if st.button("Load Claims Data", use_container_width=True, key="load_btn"):
        with st.spinner("Loading claims data..."):
            st.session_state.claims_data = load_claims_data(custom_url)
        
        if st.session_state.claims_data is not None and not st.session_state.claims_data.empty:
            st.success(f"✅ Loaded {len(st.session_state.claims_data)} claims")
        else:
            st.error("❌ Failed to load claims data")
    
    st.divider()
    
    # Filtering section
    if st.session_state.claims_data is not None and not st.session_state.claims_data.empty:
        st.subheader("🔍 Data Filters")
        
        with st.expander("Filter Options", expanded=False):
            # Amount filter
            col1, col2 = st.columns(2)
            with col1:
                min_amount = st.number_input(
                    "Min Amount",
                    min_value=0.0,
                    value=float(st.session_state.claims_data['claim_amount'].min())
                )
            with col2:
                max_amount = st.number_input(
                    "Max Amount",
                    value=float(st.session_state.claims_data['claim_amount'].max())
                )
            
            # Apply filters
            st.session_state.filtered_data = filter_claims_by_parameters(
                st.session_state.claims_data,
                min_amount=min_amount,
                max_amount=max_amount
            )
    
    st.divider()
    
    # Anomaly detection settings
    st.subheader("🚨 Anomaly Detection")
    
    anomaly_method = st.radio(
        "Detection Method:",
        ["Threshold", "Statistical (Z-Score)", "Machine Learning (Isolation Forest)"],
        key="anomaly_method"
    )
    
    if anomaly_method == "Threshold":
        anomaly_param = st.slider(
            "Claim Amount Threshold",
            min_value=100,
            max_value=5000,
            value=1000,
            step=50
        )
    elif anomaly_method == "Statistical (Z-Score)":
        anomaly_param = st.slider(
            "Z-Score Threshold",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.5
        )
    else:
        anomaly_param = st.slider(
            "Expected Anomaly Rate (%)",
            min_value=1,
            max_value=20,
            value=5
        )
    
    st.divider()
    
    # GPT settings
    st.subheader("🤖 AI Assistant")
    
    gpt_enabled = st.checkbox("Enable AI Features (requires OpenAI API key)", value=True)
    gpt_model = "gpt-3.5-turbo"  # Default model
    
    if gpt_enabled:
        gpt_model = st.selectbox(
            "GPT Model:",
            ["gpt-4", "gpt-3.5-turbo"],
            key="gpt_model"
        )
        
        # Auto-validate API connection on first run
        if not st.session_state.gpt_initialized:
            # Silent validation (verbose=False) to avoid cluttering UI
            if validate_api_connection(verbose=False):
                st.session_state.gpt_initialized = True
                st.success("✅ AI features ready!")
            else:
                st.warning("⚠️ AI features unavailable - Check your API key in settings")
    
    if st.button("Test API Connection", use_container_width=True):
        if gpt_enabled:
            with st.spinner("Testing connection..."):
                if validate_api_connection(verbose=True):
                    st.success("✅ API Connection Successful!")
                    st.session_state.gpt_initialized = True
                else:
                    st.error("❌ API Connection Failed")
        else:
            st.info("AI features disabled")

# ==================== MAIN CONTENT ====================

# Initial load message
if st.session_state.claims_data is None:
    col1, col2, col3 = st.columns(3)
    with col2:
        st.info("👈 Use the sidebar to load claims data to get started")
else:
    # Use filtered data if available, otherwise use all data
    display_data = st.session_state.filtered_data if st.session_state.filtered_data is not None else st.session_state.claims_data
    
    # ========== DATA OVERVIEW ==========
    st.header("📈 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = get_statistics(display_data)
    
    with col1:
        st.metric("Total Claims", f"{stats.get('total_claims', 0):,}")
    with col2:
        st.metric("Total Amount", f"${stats.get('total_amount', 0):,.2f}")
    with col3:
        st.metric("Avg Claim", f"${stats.get('avg_claim', 0):,.2f}")
    with col4:
        st.metric("Unique Providers", f"{stats.get('unique_providers', 0)}")
    
    # Show raw data toggle
    if st.checkbox("Show Raw Claims Data"):
        st.subheader("Raw Claims Data")
        st.dataframe(display_data, use_container_width=True, height=400)
    
    # ========== NETWORK ANALYSIS ==========
    st.header("🕸️ Patient-Provider Network Analysis")
    
    with st.spinner("Building network..."):
        network = build_patient_provider_network(display_data)
        net_stats = get_network_statistics(network)
        suspicious_clusters = detect_suspicious_clusters(network)
    
    # Display network
    st.subheader("Network Visualization")
    
    fig = create_network_visualization(
        network,
        title=f"Patient-Provider Network ({net_stats['num_nodes']} nodes, {net_stats['num_edges']} connections)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Network statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Network Nodes", net_stats['num_nodes'])
    with col2:
        st.metric("Connections", net_stats['num_edges'])
    with col3:
        st.metric("Avg Degree", f"{net_stats['avg_degree']:.2f}")
    with col4:
        st.metric("Connected Components", net_stats['num_connected_components'])
    
    # Suspicious clusters
    if suspicious_clusters['suspicious_cliques'] > 0:
        st.warning(f"⚠️ {suspicious_clusters['suspicious_cliques']} suspicious clusters detected!")
        with st.expander("View Cluster Details"):
            for i, clique in enumerate(suspicious_clusters['clique_details'], 1):
                st.write(f"**Cluster {i}** (size: {len(clique)}): {', '.join(clique[:5])}{'...' if len(clique) > 5 else ''}")
    
    # ========== ANOMALY DETECTION ==========
    st.header("🚨 Anomaly Detection & Fraud Indicators")
    
    # Check if data is valid before anomaly detection
    if display_data.empty or 'claim_amount' not in display_data.columns:
        st.warning("⚠️ Cannot perform anomaly detection: No valid data with claim_amount column available.")
    else:
        with st.spinner("Detecting anomalies..."):
            # Apply selected anomaly detection method
            if anomaly_method == "Threshold":
                anomalies = detect_anomalies_threshold(
                    display_data,
                    column='claim_amount',
                    threshold=anomaly_param
                )
            elif anomaly_method == "Statistical (Z-Score)":
                anomalies = detect_anomalies_statistical(
                    display_data,
                    column='claim_amount',
                    z_threshold=anomaly_param
                )
            else:
                anomalies = detect_anomalies_isolation_forest(
                    display_data,
                    contamination=anomaly_param / 100
                )
            
            st.session_state.anomalies = anomalies
        
        # Anomaly summary
        anomaly_summary = get_anomaly_summary(anomalies)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Anomalies", anomaly_summary['anomalies_detected'])
        with col2:
            st.metric("% of Claims", f"{anomaly_summary['anomaly_percentage']:.1f}%")
        with col3:
            st.metric("Avg Anomaly Amount", f"${anomaly_summary['avg_amount_anomaly']:,.2f}")
        with col4:
            st.metric("Avg Normal Amount", f"${anomaly_summary['avg_amount_normal']:,.2f}")
        
        # Display top anomalies
        st.subheader("Top Anomalous Claims")
        
        top_anomalies = get_top_anomalies(
            anomalies[anomalies['is_anomaly']],
            anomaly_score_col='anomaly_score',
            n=10
        )
        
        if not top_anomalies.empty:
            display_cols = ['patient_id', 'provider_id', 'claim_amount', 'diagnosis_code', 'anomaly_score']
            available_cols = [col for col in display_cols if col in top_anomalies.columns]
            
            st.dataframe(
                top_anomalies[available_cols],
                use_container_width=True,
                height=300
            )
        else:
            st.info("No anomalies detected with current parameters")
        
        # ========== GPT AI INSIGHTS ==========
        if gpt_enabled and st.session_state.gpt_initialized:
            st.header("🤖 AI-Powered Insights & Analysis")
            
            # Tabs for different AI features
            tab1, tab2, tab3 = st.tabs(["Anomaly Explanation", "Network Insights", "Ask Question"])
            
            with tab1:
                st.subheader("GPT Analysis of Top Anomaly")
                
                if st.button("Generate Explanation", key="explain_anomaly"):
                    if not top_anomalies.empty:
                        with st.spinner("Generating explanation..."):
                            top_anomaly = top_anomalies.iloc[0]
                            
                            context = f"Dataset context: {anomaly_summary['total_claims']} total claims analyzed. "
                            context += f"Anomaly detection method: {anomaly_method}"
                            
                            explanation = generate_anomaly_explanation(
                                top_anomaly,
                                context=context,
                                model=gpt_model
                            )
                            
                            if explanation:
                                st.markdown("### 📋 Analysis Result")
                                st.write(explanation)
                    else:
                        st.info("No anomalies to explain")
            
            with tab2:
                st.subheader("GPT Analysis of Network Patterns")
                
                if st.button("Generate Network Insights", key="network_insights"):
                    with st.spinner("Analyzing network patterns..."):
                        insights = generate_network_insights(
                            net_stats,
                            suspicious_clusters,
                            len(display_data),
                            model=gpt_model
                        )
                        
                        if insights:
                            st.markdown("### 🕸️ Network Analysis")
                            st.write(insights)
            
            with tab3:
                st.subheader("Ask AI About Your Claims Data")
                
                question = st.text_area(
                    "Ask a question about the claims data:",
                    placeholder="e.g., 'Which providers have the highest average claim amounts?'",
                    height=100
                )
                
                if st.button("Get Answer", key="ask_question"):
                    if question:
                        with st.spinner("Analyzing question..."):
                            claims_summary = f"""
Current Dataset:
- Total Claims: {anomaly_summary['total_claims']}
- Average Claim Amount: ${anomaly_summary['avg_amount_normal']:,.2f}
- Unique Patients: {stats['unique_patients']}
- Unique Providers: {stats['unique_providers']}
- Anomalies Detected: {anomaly_summary['anomalies_detected']}
- Detection Method: {anomaly_method}
"""
                            
                            answer = answer_claims_question(
                                question,
                                claims_summary,
                                model=gpt_model
                            )
                            
                            if answer:
                                st.markdown("### 💡 Answer")
                                st.write(answer)
                    else:
                        st.warning("Please enter a question")
        elif gpt_enabled and not st.session_state.gpt_initialized:
            st.warning("⚠️ GPT features unavailable - API connection not validated. Check sidebar settings.")
        elif gpt_enabled:
            st.info("ℹ️ AI features are disabled. Enable in the sidebar to use GPT-powered analysis.")
    
    # ========== EXPORT & REPORT ==========
    st.header("📊 Export & Reporting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Anomalies CSV", use_container_width=True):
            if st.session_state.anomalies is not None and not st.session_state.anomalies.empty:
                csv = st.session_state.anomalies[st.session_state.anomalies['is_anomaly']].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No anomalies to download")
    
    with col2:
        if st.button("Download All Claims", use_container_width=True):
            csv = display_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"claims_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        st.info("📋 Additional export formats coming soon")

# ==================== FOOTER ====================
st.divider()
st.markdown("""
---
### 📌 Important Security & Compliance Notes:

🔐 **Data Privacy**: This application processes healthcare claims data. Ensure HIPAA and other regulatory compliance.

🔑 **API Security**: Never commit API keys to version control. Use `.streamlit/secrets.toml` securely.

🌐 **Network Security**: Deploy over HTTPS with proper authentication and VPN access controls.

📊 **Data Validation**: All input data is validated and sanitized before processing.

🔍 **Explainability**: AI insights should supplement (not replace) human analyst review.

For more information, see the README.md and .github/copilot-instructions.md
""")

# 🏥 HealthClaim Analytics Hub

AI-powered patient claims fraud, waste, and abuse (FWA) detection system with interactive network visualization and GPT-4 integration.

> **🕵️‍♀️ Built Upon:** This project is a modern extension and enhancement of the innovative work from the **[Neural Nexus Healthcare Fraud Detection](https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis)** project. Originally developed for the **ITAG Atlantec Hackathon 2025** held in Galway, that project pioneered the use of graph analysis and machine learning for healthcare fraud detection. This solution modernizes and extends those concepts with a production-ready Streamlit application, advanced AI integration, and enterprise deployment support.
>
> **Original Contributors:** Primarily developed and maintained by **Nithin Mohan T K**  
> **Disclaimer:** This solution uses **synthetic data generated with Irish healthcare context** for demonstration purposes and does not represent actual claims data. It is intended for learning and personal development only.

## 📋 Overview

HealthClaim Analytics Hub is a Streamlit web application designed to help healthcare fraud investigators and analysts:

- **Visualize** patient-provider interaction networks to identify suspicious clusters and referral patterns
- **Detect** anomalous claims using multiple statistical and ML-based methods
- **Analyze** suspicious patterns with AI-powered explanations using OpenAI's GPT models
- **Investigate** fraud rings through interactive filtering and drill-down capabilities
- **Comply** with HIPAA and healthcare data security standards

## 🎯 Key Features

### 🕸️ Network Analysis
- Interactive patient-provider network visualization using Plotly
- Automatic detection of suspicious cliques and highly connected clusters
- Network metrics: density, connectivity, connected components
- Spring-layout visualization optimized for pattern discovery

### 🚨 Anomaly Detection (3 Methods)
1. **Threshold-based**: Simple claim amount filtering
2. **Statistical (Z-Score)**: Deviation-based anomaly flagging
3. **Isolation Forest**: ML-based outlier detection for complex patterns

### 🤖 AI-Powered Insights
- **Anomaly Explanation**: GPT-4 analysis of suspicious claims
- **Network Insights**: AI interpretation of network patterns and fraud rings
- **Q&A Interface**: Ask questions about claims data patterns
- **Actionable Recommendations**: Investigation priorities and next steps

### 📊 Data Management
- CSV data loading with validation and sanitization
- Advanced filtering: amount ranges, date ranges, patient/provider IDs
- Data quality checks and cleaning
- Export functionality for anomalies and reports

### 🔐 Security & Compliance
- API key management via `st.secrets` (no hardcoded keys)
- HIPAA-aware data handling
- Data validation and sanitization
- Audit-ready logging and analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for AI features)
- pip or conda

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd python-streamlit-gpt-dataviz-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure secrets:**
```bash
# Copy the example secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit the file and add your OpenAI API key
# .streamlit/secrets.toml:
# OPENAI_API_KEY = "sk-..."
```

5. **Run the application:**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Load Claims Data
1. Open the sidebar **Control Panel**
2. Click **Load Claims Data**
- Default loads sample data from neural-nexus repo
- Or upload your own CSV file

### Step 2: Configure Filters & Detection
1. Set **Data Filters** (amount range, date range)
2. Choose **Anomaly Detection Method**:
   - Threshold (simple, fastest)
   - Statistical Z-Score (medium complexity)
   - Isolation Forest (advanced ML-based)
3. Adjust sensitivity parameters

### Step 3: Review Network Analysis
- View patient-provider network visualization
- Identify suspicious clusters (cliques)
- Review network statistics and density

### Step 4: Analyze Anomalies
- Review top 10 anomalous claims
- View anomaly statistics and distribution
- Identify patterns in amount, frequency, providers

### Step 5: Use AI Insights (if enabled)
- **Anomaly Explanation**: Get GPT-4 analysis of top anomaly
- **Network Insights**: Understand fraud ring patterns
- **Ask Question**: Query data patterns in natural language

### Step 6: Export Results
- Download anomalies as CSV
- Export full filtered dataset
- Share findings with investigation team

## 🏗️ Architecture

```
python-streamlit-gpt-dataviz-agent/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml.example       # API key template (DO NOT COMMIT secrets.toml)
│
├── utils/                          # Reusable modules
│   ├── data.py                    # Data loading and validation
│   ├── network.py                 # Network building and visualization
│   ├── anomaly.py                 # Anomaly detection algorithms
│   └── gpt.py                     # OpenAI GPT integration
│
├── pages/                          # Multi-page apps (Streamlit feature)
│   └── [future extensions]
│
└── .github/
    └── copilot-instructions.md    # AI coding agent guidelines
```

## 🔧 Configuration

### Streamlit Config (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
font = "sans serif"

[server]
port = 8501
headless = true
maxUploadSize = 200
```

### Secrets (.streamlit/secrets.toml)
⚠️ **NEVER commit this file to git**

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

## 📊 Data Format

Expected CSV format for claims data:

| Column | Type | Description |
|--------|------|-------------|
| patient_id | int | Unique patient identifier |
| provider_id | int | Unique provider identifier |
| claim_amount | float | Claim amount in dollars |
| diagnosis_code | string | ICD-10 diagnosis code |
| procedure_code | string (optional) | CPT procedure code |
| date | datetime (optional) | Claim date |

### Example:
```csv
patient_id,provider_id,claim_amount,diagnosis_code,procedure_code,date
101,501,1250.00,I10,99213,2023-01-15
102,502,2500.00,E11,99214,2023-01-16
```

## 🧠 Anomaly Detection Methods

### Threshold Method
- **Speed**: Fastest ⚡
- **Complexity**: Simple
- **Use Case**: Quick screening, known thresholds
- **Parameter**: Claim amount threshold (e.g., $1,000)

### Statistical Z-Score
- **Speed**: Very Fast ⚡⚡
- **Complexity**: Medium
- **Use Case**: Normally distributed data, standard deviation outliers
- **Parameter**: Z-score threshold (default: 3.0 = 3 std devs from mean)

### Isolation Forest (ML)
- **Speed**: Fast ⚡⚡⚡
- **Complexity**: Advanced
- **Use Case**: Complex patterns, non-normal distributions, multi-feature analysis
- **Parameter**: Expected anomaly rate (default: 5%)

**Recommendation**: Start with Z-Score for initial exploration, then use Isolation Forest for deeper analysis.

## 🤖 AI Features

### Prerequisites
- OpenAI API account with GPT-4 or GPT-3.5-turbo access
- Valid API key in `.streamlit/secrets.toml`

### Features
1. **Anomaly Explanation**
   - Analyzes top detected anomaly
   - Provides fraud risk assessment
   - Suggests investigation priorities

2. **Network Insights**
   - Identifies fraud ring patterns
   - Flags suspicious clustering
   - Recommends investigation pathways

3. **Q&A Interface**
   - Ask questions about claims patterns
   - Get data-driven answers
   - Identify investigative leads

### Models
- **gpt-4**: Most capable, recommended for complex analysis
- **gpt-3.5-turbo**: Faster, cost-effective for volume

### Cost Estimation
- Typical API costs: $0.01-$0.05 per analysis
- Batch analysis: $1-$10 per 100 claims

## 🔐 Security & Compliance

### HIPAA Compliance
- ✅ Data validation and sanitization
- ✅ No PII stored in logs
- ✅ API key encryption
- ⚠️ Your responsibility: Network security, Access controls, Data at rest encryption

### Deployment Recommendations

**Development**
```bash
streamlit run app.py  # Local development only
```

**Production**
```bash
# Use Streamlit Cloud with authentication
# https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-cloud

# Or self-hosted with:
streamlit run app.py --server.headless true --logger.level=warning
```

**Network Security**
- Deploy behind HTTPS/TLS only
- Use VPN or corporate network
- Implement role-based access control (RBAC)
- Monitor access logs

### Data Security
- Store API keys in secure secret management (AWS Secrets Manager, Azure Key Vault)
- Encrypt data in transit (HTTPS/TLS 1.3+)
- Encrypt data at rest if storing on disk
- Use separate API keys for different environments
- Rotate API keys regularly

## 🧪 Testing

### Unit Tests (Coming Soon)
```bash
pytest tests/
```

### Integration Tests
```bash
streamlit run app.py --logger.level=debug
```

## 📈 Performance Optimization

### Caching
- Data loading uses `@st.cache_data` with 1-hour TTL
- Network visualization cached automatically
- Large datasets: Consider database backend

### Scaling
- **Small dataset** (<10K claims): Single instance
- **Medium dataset** (10K-100K): Add caching layer
- **Large dataset** (>100K): Database + async processing

## 🐛 Troubleshooting

### OpenAI API Errors
```
❌ "Authentication failed"
→ Check OPENAI_API_KEY in .streamlit/secrets.toml

❌ "Rate limit reached"
→ Wait a moment, then retry. Consider upgrading API tier.

❌ "Context length exceeded"
→ Use GPT-4 or provide less context in questions
```

### Data Loading Errors
```
❌ "Missing required columns"
→ Ensure CSV has: patient_id, provider_id, claim_amount, diagnosis_code

❌ "Connection timeout"
→ GitHub data source may be unavailable. Try uploading local CSV.
```

### Performance Issues
```
❌ "App running slowly"
→ Clear Streamlit cache: rm -rf ~/.streamlit/cache
→ Reduce dataset size with filters
→ Use faster anomaly detection (Threshold method)
```

## 📚 API Reference

### Data Module (`utils/data.py`)
```python
# Load claims data
claims_df = load_claims_data()

# Filter claims
filtered = filter_claims_by_parameters(
    df=claims_df,
    min_amount=1000,
    max_amount=5000
)

# Get statistics
stats = get_statistics(claims_df)
```

### Network Module (`utils/network.py`)
```python
# Build network
G = build_patient_provider_network(claims_df)

# Visualize
fig = create_network_visualization(G)

# Get statistics
net_stats = get_network_statistics(G)
```

### Anomaly Module (`utils/anomaly.py`)
```python
# Threshold-based
anomalies = detect_anomalies_threshold(df, threshold=1000)

# Statistical
anomalies = detect_anomalies_statistical(df, z_threshold=3.0)

# ML-based
anomalies = detect_anomalies_isolation_forest(df, contamination=0.05)
```

### GPT Module (`utils/gpt.py`)
```python
# Explain anomaly
explanation = generate_anomaly_explanation(claim_row)

# Network insights
insights = generate_network_insights(stats, clusters, total_claims)

# Ask question
answer = answer_claims_question(question, context)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This application is a **decision support tool** and should **NOT** be the sole basis for fraud investigation decisions. Always:

- ✅ Use AI insights as leads for human analysts to investigate
- ✅ Validate all detected anomalies with domain experts
- ✅ Follow proper legal and regulatory procedures
- ✅ Document investigation decisions and reasoning
- ⚠️ Do NOT automatically act on AI recommendations
- ⚠️ Do NOT share findings without proper authorization

## 🆘 Support & Issues

- **Documentation**: See this README and `.github/copilot-instructions.md`
- **Issues**: Open a GitHub issue with details
- **Questions**: Check existing issues and documentation first

## 🎓 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [NetworkX Guide](https://networkx.org/)
- [Plotly Charts](https://plotly.com/python/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [HIPAA Compliance](https://www.hhs.gov/hipaa)
- [Healthcare Fraud Detection](https://oig.hhs.gov/)

---

**Last Updated**: November 2, 2025

**Version**: 1.0.0  
**Status**: Production Ready

**Current Maintainer**: AI Development Team  
**Original Creator**: Nithin Mohan T K (Neural Nexus - ITAG Atlantec Hackathon 2025)

**Related Projects**:
- [Neural Nexus Healthcare Fraud Detection](https://github.com/HackmaniaGX/neural-nexus-healthcare-fwa-analysis) - Original project
- [ITAG Atlantec Hackathon 2025](https://itagatlantec.ie/) - Hackathon information

**Note**: This project is a modernized extension of the Neural Nexus work. All sample data is synthetic and generated for demonstration purposes only. This is a personal learning project and does not represent any employer's work or knowledge.

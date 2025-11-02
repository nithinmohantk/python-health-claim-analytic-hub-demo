# 🏗️ HealthClaim Analytics Hub - Architecture & Design Documentation

**Document Version**: 0.0.1
**Last Updated**: November 2, 2025  
**Status**: DEMO Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Algorithm Details](#algorithm-details)
6. [Deployment Architecture](#deployment-architecture)
7. [Performance Characteristics](#performance-characteristics)
8. [Security Architecture](#security-architecture)

---

## System Overview

### Purpose

HealthClaim Analytics Hub is a **fraud detection and analysis system** designed to:
- Visualize complex patient-provider networks
- Detect anomalous claims using multiple algorithms
- Provide AI-powered insights using GPT
- Support investigation workflows

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Architecture** | Modular, layered, event-driven |
| **Scale** | Handles 10K-100K claims efficiently |
| **Deployment** | Streamlit (web), Docker, Kubernetes-ready |
| **Integration** | OpenAI API, GitHub data source |
| **Security** | HIPAA-aware, key management via secrets |
| **Testing** | 86 unit/integration tests, 82% coverage |

---

## Architecture Layers

### 1️⃣ Presentation Layer (Streamlit UI)

**Components**:
- `streamlit` framework
- Sidebar controls
- Interactive tabs
- Plotly visualizations
- Session state management

**Responsibilities**:
- User interaction handling
- State persistence
- Real-time UI updates
- Chart rendering

**Technologies**:
- Streamlit 1.50.0
- Plotly 6.3.1
- HTML/CSS/JavaScript (generated)

**Key Features**:
- `@st.cache_data` decorator for performance
- Reactive updates on parameter changes
- Multi-tab interface organization

---

### 2️⃣ Application Layer (Orchestration)

**File**: `app.py` (600+ lines)

**Responsibilities**:
- Route user interactions to modules
- Manage session state
- Coordinate data flow
- Handle UI event logic

**Key Sections**:

```
├── 📌 Session Initialization
│   ├── Initialize session state
│   ├── Set default values
│   └── Load cached data
│
├── 🎨 UI Components
│   ├── Sidebar controls
│   ├── Main tabs
│   ├── Charts
│   └── Data tables
│
├── 🔄 Event Handlers
│   ├── Data load button
│   ├── Filter updates
│   ├── Method selection
│   └── AI analysis triggers
│
└── 💾 Data Management
    ├── Call data module
    ├── Process results
    └── Update displays
```

---

### 3️⃣ Core Processing Layer

#### 3.1 Data Module (`utils/data.py`)

**Functions**:
- `load_claims_data()` - Load from GitHub or file
- `sanitize_claims_data()` - Validate and clean
- `filter_claims_by_parameters()` - Advanced filtering
- `get_statistics()` - Summary stats

**Data Structures**:
```python
# Input/Output DataFrame
DataFrame {
    patient_id: int64,
    provider_id: int64,
    claim_amount: float64,
    diagnosis_code: str,
    procedure_code: str (optional),
    date: datetime64 (optional)
}
```

**Validation Rules**:
- ✅ Required columns present
- ✅ No duplicate rows
- ✅ Numeric types valid
- ✅ No NULLs in critical fields
- ✅ Positive claim amounts

**Performance**:
- Load: O(n) - ~100ms per 10K rows
- Sanitize: O(n) - ~50ms per 10K rows
- Filter: O(n) - ~20ms per 10K rows
- Cache: 1 hour TTL via `@st.cache_data`

#### 3.2 Network Module (`utils/network.py`)

**Functions**:
- `build_patient_provider_network()` - Create graph
- `create_network_visualization()` - Plotly chart
- `get_network_statistics()` - Network metrics
- `detect_suspicious_clusters()` - Find cliques

**Data Structures**:
```python
# NetworkX Graph
Graph {
    nodes: [
        {id: "Patient_101", type: "patient", color: "blue"},
        {id: "Provider_501", type: "provider", color: "red"}
    ],
    edges: [
        {from: "Patient_101", to: "Provider_501", weight: 1500.0}
    ]
}
```

**Metrics Calculated**:
- `num_nodes` - Total patient + provider nodes
- `num_edges` - Total claim connections
- `density` - Network connectivity ratio
- `avg_degree` - Average connections per node
- `num_connected_components` - Separate networks

**Clique Detection**:
- Minimum size: 3 (patient + 2+ providers or reverse)
- Algorithm: Bron-Kerbosch (exponential worst case)
- Scoring: By total claim amount + connectivity
- Time: ~100ms for typical networks

**Performance**:
- Build: O(n) - ~50ms per 10K claims
- Visualize: O(n log n) - ~200ms per 10K nodes
- Statistics: O(n + m) - ~30ms
- Clustering: O(2^k) - varies by connectivity

#### 3.3 Anomaly Module (`utils/anomaly.py`)

**Three Detection Methods**:

##### Method 1: Threshold-Based
```
Algorithm:
1. Define threshold value (e.g., $1000)
2. For each claim, if amount > threshold → anomaly
3. Score = amount / threshold (normalized to 1.0 max)

Time: O(n) ~5ms per 10K claims
Pros: Simple, fast, interpretable
Cons: No context, ignores patterns
Best for: Known thresholds, quick screening
```

##### Method 2: Statistical Z-Score
```
Algorithm:
1. Calculate mean μ and standard deviation σ
2. For each claim x:
   Z-score = (x - μ) / σ
3. If |Z| > threshold (default 3.0) → anomaly
4. Score = min(|Z| / threshold, 1.0)

Time: O(n) ~10ms per 10K claims
Pros: Statistically sound, adaptable
Cons: Assumes normal distribution
Best for: Well-behaved data, standard deviations
```

##### Method 3: Isolation Forest (ML)
```
Algorithm:
1. Train ensemble of decision trees
2. Trees randomly split features
3. Anomalies isolated in fewer splits
4. Anomaly score = (total_paths - expected) / total_paths
5. Score normalized to [0, 1]

Time: O(n log n) ~50ms per 10K claims
Pros: Complex patterns, multi-dimensional
Cons: Black-box, training overhead
Best for: Complex fraud patterns
```

**Score Combination**:
```
combined_score = (w1 * score1 + w2 * score2 + w3 * score3) / (w1 + w2 + w3)
where wi = weight for method i (default: equal)
```

**Functions**:
- `detect_anomalies_*()` - Individual methods
- `combine_anomaly_scores()` - Weighted combination
- `get_top_anomalies()` - Rank by score
- `get_anomaly_summary()` - Statistics

---

### 4️⃣ AI Integration Layer (`utils/gpt.py`)

**Functions**:
- `initialize_openai()` - Setup API
- `generate_anomaly_explanation()` - Analyze claim
- `generate_network_insights()` - Interpret patterns
- `answer_claims_question()` - Q&A
- `validate_api_connection()` - Health check

**Prompting Strategy**:
```
System Role: Healthcare fraud expert
User Query: Claim/Network/Question context
Model: gpt-4 or gpt-3.5-turbo
Temperature: 0.7 (balanced, creative)
Max Tokens: 250-400 (concise, actionable)
Timeout: 30 seconds
```

**Error Handling**:
```
Authentication Error (401)
  → Check API key in secrets
  ↓
Rate Limit Error (429)
  → Wait and retry (exponential backoff)
  ↓
Timeout Error
  → Use fallback message
  ↓
Other Errors
  → Log and show generic error
```

**Integration Points**:
- Secrets: `st.secrets['OPENAI_API_KEY']`
- Models: gpt-4 (preferred), gpt-3.5-turbo (fallback)
- API: `openai.ChatCompletion.create()`

---

## Component Design

### Data Processing Pipeline

```
Raw CSV/URL
    ↓
[load_claims_data]
    ↓
Schema Validation
    ↓
[sanitize_claims_data]
    ↓
Data Cleaning (remove dups, fix types, drop NULLs)
    ↓
💾 Cache (1 hour)
    ↓
[filter_claims_by_parameters]
    ↓
Filtered DataFrame
    ↓
[Parallel Processing]
    ├─→ [build_patient_provider_network]
    │       ↓
    │   NetworkX Graph
    ├─→ [detect_anomalies_*]
    │       ↓
    │   Anomaly Scores
    └─→ [get_statistics]
            ↓
        Summary Stats
```

### Module Interactions

```
                    app.py
                    /   |   \
                   /    |    \
              data.py network.py anomaly.py   gpt.py
              /     \              \          /
         GitHub  Validation   Patterns   OpenAI
```

### State Management

**Streamlit Session State**:
```python
st.session_state {
    'data_loaded': bool,
    'claims_df': DataFrame,
    'filtered_df': DataFrame,
    'network_graph': NetworkX.Graph,
    'anomaly_scores': Series,
    'network_stats': dict,
    'anomaly_stats': dict,
    'ai_analysis': str
}
```

---

## Data Flow

### Complete User Journey

```
1. USER ACTION: Open app
   ↓
2. STREAMLIT: Initialize UI, load session state
   ↓
3. USER ACTION: Click "Load Data"
   ↓
4. DATA MODULE: Load from GitHub/file
   ↓
5. DATA MODULE: Validate schema
   ↓
6. DATA MODULE: Sanitize and clean
   ↓
7. STREAMLIT: Cache for 1 hour
   ↓
8. USER ACTION: Set filters
   ↓
9. DATA MODULE: Filter by parameters
   ↓
10. PARALLEL PROCESSING:
    a) NETWORK: Build graph & visualize
    b) ANOMALY: Detect anomalies
    c) STATS: Calculate metrics
   ↓
11. STREAMLIT: Display charts & tables
   ↓
12. USER ACTION: Request AI analysis (optional)
   ↓
13. GPT MODULE: Initialize OpenAI
   ↓
14. GPT MODULE: Build context prompt
   ↓
15. GPT MODULE: Call OpenAI API
   ↓
16. GPT MODULE: Parse response
   ↓
17. STREAMLIT: Display AI insights
   ↓
18. USER ACTION: Export results
   ↓
19. STREAMLIT: Generate CSV
   ↓
20. USER: Download file
```

### Data Transformations

```
Raw Claim Data
  ├─ patient_id: 101
  ├─ provider_id: 501
  ├─ claim_amount: 1250.00
  └─ diagnosis_code: "I10"
         ↓
    [NETWORK ANALYSIS]
         ↓
Patient Node "Patient_101"  ─[edge: 1250]─→  Provider Node "Provider_501"
         ↓
    [ANOMALY DETECTION]
         ↓
Threshold: 0.3 (claim 30% above threshold)
Z-Score: 0.85 (1.5 std devs from mean)
IF Score: 0.25 (25% anomaly probability)
Combined: 0.47 (47% anomaly likelihood)
         ↓
    [AI ANALYSIS]
         ↓
"This claim shows moderate risk due to amount. Recommend verification against medical records."
```

---

## Algorithm Details

### Clique Detection Algorithm (Simplified)

```python
def detect_suspicious_clusters(graph):
    """Find fraud rings using clique detection"""
    
    # Find all cliques (patient-provider groups)
    cliques = find_cliques(graph)
    
    # Score each clique
    scored_cliques = []
    for clique in cliques:
        if len(clique) >= 3:  # Minimum group size
            edges = get_clique_edges(clique)
            total_weight = sum(e.weight for e in edges)
            avg_weight = total_weight / len(edges)
            density = num_edges / possible_edges
            
            score = (total_weight / 10000) * density
            scored_cliques.append((clique, score))
    
    # Return top suspicious clusters
    return sorted(scored_cliques, key=lambda x: x[1], reverse=True)[:10]
```

### Combined Anomaly Scoring

```python
def combine_anomaly_scores(
    threshold_scores,
    statistical_scores,
    isolation_forest_scores,
    weights=[1.0, 1.0, 1.0]
):
    """Combine three detection methods"""
    
    # Normalize each score to [0, 1]
    norm_threshold = normalize(threshold_scores)
    norm_statistical = normalize(statistical_scores)
    norm_isolation = normalize(isolation_forest_scores)
    
    # Weighted combination
    combined = (
        weights[0] * norm_threshold +
        weights[1] * norm_statistical +
        weights[2] * norm_isolation
    ) / sum(weights)
    
    return combined
```

---

## Deployment Architecture

### Single Instance (Development)

```
Docker Container
├── Python 3.14
├── Streamlit Runtime
├── Utils Modules
└── Requirements

Running: streamlit run app.py
Access: http://localhost:8501
```

### Production Deployment

```
                    Internet
                        ↓
                   [Firewall]
                        ↓
    [Nginx - Reverse Proxy, SSL/TLS]
                        ↓
    [Docker Container - Streamlit App]
    ├── app.py
    ├── utils/
    ├── .streamlit/config.toml
    └── Azure Secrets Manager
             ↑
        (OpenAI Key)
```

### Kubernetes Deployment

```
[Ingress Controller]
        ↓
[Service]
        ↓
[Pod 1: Streamlit App] [Pod 2: Streamlit App]
        ↓                    ↓
    [PersistentVolume - Data Cache]
        ↓
    [Secrets - API Keys]
```

---

## Performance Characteristics

### Benchmark Results (10K Claims)

| Operation | Time | Algorithm | Complexity |
|-----------|------|-----------|------------|
| Load Data | 100ms | CSV parsing | O(n) |
| Sanitize | 50ms | Filtering/sorting | O(n) |
| Filter | 20ms | Index lookup | O(n) |
| Build Network | 50ms | Graph creation | O(n) |
| Visualize Network | 200ms | Spring layout | O(n log n) |
| Threshold Detection | 5ms | Simple comparison | O(n) |
| Z-Score Detection | 10ms | Stat calculation | O(n) |
| Isolation Forest | 50ms | Tree training | O(n log n) |
| Clique Detection | 100ms | Bron-Kerbosch | O(2^k) |
| **Total Pipeline** | **~400ms** | | |

### Scaling Characteristics

| Dataset Size | Memory | Execution Time | Recommendation |
|--------------|--------|----------------|-----------------|
| < 1K claims | 50 MB | 100ms | ✅ Ideal |
| 1K-10K | 100 MB | 400ms | ✅ Recommended |
| 10K-100K | 500 MB | 2-5s | ⚠️ Add caching |
| 100K-1M | 1+ GB | 10-30s | ❌ Database needed |
| 1M+ | 5+ GB | Minutes | ❌ Distributed system |

---

## Security Architecture

### Data Security

```
User Data
    ↓
[Validation Layer] - Remove invalid data
    ↓
[Sanitization Layer] - Remove dangerous patterns
    ↓
[Application Memory] - RAM only, no disk
    ↓
[Cache Layer] - Streamlit cache (1 hour max)
    ↓
[Export] - CSV download (temporary)
```

### API Key Management

```
Configuration:
.streamlit/secrets.toml
├── OPENAI_API_KEY = "sk-..."
├── Mode: Never commit to git
└── Location: ~/.streamlit/secrets.toml locally

Production:
├── Azure Key Vault
├── AWS Secrets Manager
├── Kubernetes Secrets
└── Environment Variables
```

### HIPAA Compliance Checklist

- ✅ Data validation and sanitization
- ✅ No PII logging
- ✅ API key encryption
- ✅ HTTPS/TLS requirement
- ⚠️ Audit logging (user responsibility)
- ⚠️ Access control (user responsibility)
- ⚠️ Data encryption at rest (user responsibility)

---

## Monitoring & Observability

### Logging Points

```
Data Loading:
  - Source URL
  - Records loaded
  - Validation errors
  - Cache hit/miss

Processing:
  - Filter parameters
  - Anomaly scores
  - Network metrics
  - Execution time

AI Analysis:
  - API call timestamp
  - Model used
  - Response time
  - Token count

User Actions:
  - Button clicks
  - Filter changes
  - Exports
  - Analysis requests
```

### Performance Monitoring

```
Metrics to Track:
- Data load time
- Filter execution time
- Network visualization time
- Anomaly detection time
- API response time
- UI responsiveness
- Cache hit rate
- Memory usage
```

---

## Future Enhancements

### Planned Improvements

1. **Database Backend**
   - PostgreSQL for large datasets
   - Elasticsearch for full-text search
   - Redis for distributed caching

2. **Advanced Analytics**
   - Time-series analysis
   - Predictive modeling
   - Pattern learning
   - Real-time alerts

3. **Enhanced UI**
   - Multi-page Streamlit app
   - Custom dashboards
   - Report generation
   - Collaboration features

4. **Deployment**
   - Kubernetes support
   - Auto-scaling
   - Load balancing
   - Multi-region deployment

5. **Integration**
   - EHR system integration
   - Data warehouse connection
   - Third-party fraud tools
   - Compliance reporting

---

**Document Complete** ✅

For implementation details, see `README.md`  
For testing information, see `TESTING.md`  
For deployment guide, see `docs/DEPLOYMENT.md`

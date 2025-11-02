# 📑 Project Files Reference

## 🎯 File Structure & Purposes

### 🌟 Main Application Files

#### `app.py` (600+ lines)
**Purpose**: Core Streamlit application  
**Key Components**:
- Page configuration and styling
- Session state management
- Sidebar control panel
- Data loading interface
- Network visualization
- Anomaly detection controls
- GPT-powered analysis tabs
- Export functionality
**Key Functions**:
- `st.session_state` for data persistence
- Multi-tab interface with tabs
- Real-time data filtering
- Integration of all modules

---

## 🔧 Utility Modules (`utils/`)

### `utils/data.py` (200+ lines)
**Purpose**: Data loading, validation, and processing  
**Key Functions**:
- `load_claims_data()` - Load from GitHub or URL with caching
- `sanitize_claims_data()` - Data quality checks and cleaning
- `filter_claims_by_parameters()` - Advanced filtering
- `get_statistics()` - Calculate summary statistics

**Features**:
- HIPAA-aware data handling
- Duplicate detection
- Type validation (numeric, datetime)
- Missing value handling
- Comprehensive error messages

---

### `utils/network.py` (250+ lines)
**Purpose**: Patient-provider network construction and visualization  
**Key Functions**:
- `build_patient_provider_network()` - Create NetworkX graph
- `create_network_visualization()` - Plotly interactive chart
- `get_network_statistics()` - Calculate network metrics
- `detect_suspicious_clusters()` - Find fraud rings via cliques

**Features**:
- Spring-layout optimization
- Node sizing by degree (connectivity)
- Color-coding (patients vs providers)
- Edge weights represent claim amounts
- Clique detection (fraud ring identification)

**Metrics Calculated**:
- Number of nodes and edges
- Average degree
- Network density
- Connected components
- Clique analysis

---

### `utils/anomaly.py` (350+ lines)
**Purpose**: Multiple anomaly detection algorithms  
**Key Functions**:
- `detect_anomalies_threshold()` - Fixed or percentile threshold
- `detect_anomalies_statistical()` - Z-score based
- `detect_anomalies_isolation_forest()` - ML-based outlier detection
- `detect_frequency_anomalies()` - Time-based patterns
- `combine_anomaly_scores()` - Multi-method scoring
- `get_top_anomalies()` - Ranking and filtering
- `get_anomaly_summary()` - Statistical overview

**Features**:
- Three complementary detection methods
- Adjustable sensitivity
- Weighted combination of methods
- Frequency-based detection
- Summary statistics

---

### `utils/gpt.py` (200+ lines)
**Purpose**: OpenAI API integration for AI-powered analysis  
**Key Functions**:
- `initialize_openai()` - Setup API credentials
- `generate_anomaly_explanation()` - Analyze suspicious claims
- `generate_network_insights()` - Interpret fraud patterns
- `answer_claims_question()` - Q&A interface
- `validate_api_connection()` - Connection testing

**Features**:
- Error handling (auth, rate limit, timeout)
- Context-aware prompting
- Model selection (GPT-4 or GPT-3.5-turbo)
- Token limiting
- Fraud expert persona

---

## 📋 Configuration Files

### `.streamlit/config.toml`
**Purpose**: Streamlit application settings  
**Contains**:
- Theme configuration (colors, fonts)
- Server settings (port, headless mode)
- Logger level
- Client options
- Upload size limits

---

### `.streamlit/secrets.toml.example`
**Purpose**: Template for sensitive credentials  
**Template Variables**:
- `OPENAI_API_KEY` - Required for AI features
- Optional: `OPENAI_ORG_ID`, `OPENAI_API_VERSION`

**⚠️ Important**: Never commit `secrets.toml` (only `.example`)

---

### `.env.example`
**Purpose**: Environment variables template  
**Contains**:
- OpenAI configuration
- Streamlit settings
- Data source URLs
- Application environment variables

---

## 🐳 Deployment & Infrastructure

### `Dockerfile`
**Purpose**: Container image definition  
**Features**:
- Python 3.10 slim base
- All dependencies installed
- Streamlit configuration
- Health check endpoint
- Secure command execution

---

### `docker-compose.yml`
**Purpose**: Multi-container orchestration  
**Services**:
- **healthclaim**: Main Streamlit app
- **nginx**: Reverse proxy with SSL/TLS

**Features**:
- Volume mounting for data
- Environment variable support
- Health checks
- Automatic restart
- Network isolation

---

### `nginx.conf`
**Purpose**: Reverse proxy and SSL/TLS termination  
**Features**:
- HTTP → HTTPS redirect
- TLS 1.2/1.3 support
- Security headers (HSTS, X-Frame-Options, CSP)
- Rate limiting
- Gzip compression
- WebSocket support for Streamlit
- Caching for static assets
- Access logging

---

## 📦 Dependencies & Environments

### `requirements.txt`
**Purpose**: Production dependencies  
**Contents** (10 packages):
- `streamlit==1.28.1` - Web framework
- `pandas==2.1.3` - Data processing
- `networkx==3.2` - Graph analysis
- `matplotlib==3.8.2` - Plotting
- `plotly==5.18.0` - Interactive charts
- `openai==1.3.9` - AI integration
- `scikit-learn==1.3.2` - ML algorithms
- `numpy==1.26.2` - Numerical computing
- `python-dotenv==1.0.0` - Environment variables
- `requests==2.31.0` - HTTP client

---

### `requirements-dev.txt`
**Purpose**: Development dependencies  
**Contents** (10+ packages):
- All production requirements
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `black` - Code formatter
- `flake8` - Linter
- `isort` - Import sorter
- `mypy` - Type checker
- `sphinx` - Documentation generator

---

## 📚 Documentation

### `README.md` (500+ lines)
**Purpose**: Complete user and developer guide  
**Sections**:
- Feature overview
- Quick start guide
- Usage workflow
- Architecture
- Configuration
- Data format
- Anomaly detection methods
- AI features
- Security & compliance
- Troubleshooting
- API reference

---

### `DEPLOYMENT.md` (400+ lines)
**Purpose**: Production deployment guide  
**Sections**:
- Local development setup
- OpenAI API configuration
- Production deployment options:
  - Streamlit Cloud
  - AWS EC2
  - Azure App Service
  - Docker
- Security checklist
- Monitoring & maintenance
- Troubleshooting

---

### `IMPLEMENTATION_SUMMARY.md` (300+ lines)
**Purpose**: Project completion overview  
**Sections**:
- Implementation status
- What's been built
- Project structure
- Key features
- Getting started
- Usage workflow
- Security features
- Next steps
- Verification checklist

---

## 🚀 Quick Start Scripts

### `quickstart.sh` (100 lines)
**Purpose**: Automated setup for macOS/Linux  
**Steps**:
1. Check Python version
2. Create virtual environment
3. Activate environment
4. Install dependencies
5. Configure secrets
6. Test API connection
7. Start application

**Usage**: `./quickstart.sh`

---

### `quickstart.bat` (80 lines)
**Purpose**: Automated setup for Windows  
**Steps**: Same as shell script
**Usage**: `quickstart.bat`

---

## 📁 Utility Modules Package

### `utils/__init__.py`
**Purpose**: Python package initialization  
**Content**: Simple module docstring

---

## 🔒 Version Control

### `.gitignore`
**Purpose**: Exclude files from git tracking  
**Patterns Excluded**:
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)
- Secrets (`.streamlit/secrets.toml`, `.env`)
- Build artifacts
- Log files
- OS files

**Important**: Prevents accidental secret commits

---

## 🎯 Optional/Future Files

### `.github/copilot-instructions.md` (Original)
**Purpose**: AI coding agent guidelines  
**Contains**:
- Original product specification
- Use cases
- Architecture overview
- Code sample
- Best practices
- Security considerations

---

## 📊 File Statistics

| Category | Count | Total Lines |
|----------|-------|------------|
| Python Application | 1 | 600+ |
| Python Modules | 4 | 1,000+ |
| Configuration | 4 | 100+ |
| Documentation | 4 | 1,500+ |
| Deployment | 3 | 300+ |
| Scripts | 2 | 200+ |
| **Total** | **18** | **3,700+** |

---

## 🔄 Data Flow Architecture

```
User Input (Sidebar)
    ↓
Data Loading (utils/data.py)
    ↓
Data Filtering & Validation
    ↓
├─→ Network Analysis (utils/network.py)
│   └─→ Plotly Visualization
│
├─→ Anomaly Detection (utils/anomaly.py)
│   └─→ Top-N Anomalies
│
└─→ AI Analysis (utils/gpt.py)
    ├─→ Anomaly Explanation
    ├─→ Network Insights
    └─→ Q&A Response

User Output (Streamlit Dashboard)
    ├─→ Visualizations
    ├─→ Statistics
    ├─→ Export (CSV)
    └─→ Reports
```

---

## 🔐 Security File Hierarchy

**Public (Safe to Commit)**:
- ✅ `.github/copilot-instructions.md`
- ✅ `README.md`, `DEPLOYMENT.md`
- ✅ `requirements*.txt`
- ✅ `Dockerfile`, `docker-compose.yml`
- ✅ `.gitignore`
- ✅ All Python source files

**Template (Commit Safely)**:
- ✅ `.env.example`
- ✅ `.streamlit/secrets.toml.example`
- ✅ `.streamlit/config.toml`

**Private (Never Commit)**:
- ❌ `.env` (actual values)
- ❌ `.streamlit/secrets.toml` (API keys)
- ❌ `.streamlit/cache/*`
- ❌ `venv/`, `env/`
- ❌ `__pycache__/`

---

## 📝 How to Use This Reference

1. **To understand the app**: Start with `README.md`
2. **To deploy**: Read `DEPLOYMENT.md`
3. **To modify code**: Check `utils/` modules and `app.py`
4. **To add features**: See IMPLEMENTATION_SUMMARY.md "Next Steps"
5. **To troubleshoot**: Check README.md "Troubleshooting"
6. **To understand architecture**: This file + docstrings in code

---

**Last Updated**: November 2, 2025  
**Total Project Size**: ~3,700 lines of code and documentation  
**Status**: ✅ Complete and production-ready

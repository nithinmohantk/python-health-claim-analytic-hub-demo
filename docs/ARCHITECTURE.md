# Architecture Documentation

This document provides an overview of the architecture diagrams available in the draw.io file.

## Architecture Diagrams

All architecture diagrams are maintained in a single draw.io file: **`docs/architecture.drawio`**

This file serves as the **single source of truth** for all architectural documentation and can be opened in:
- [draw.io](https://app.diagrams.net/) (web)
- [draw.io Desktop](https://github.com/jgraph/drawio-desktop)
- VS Code with draw.io extension

## Available Diagrams

### 1. C4 Context Diagram
**Purpose**: High-level system overview showing the system and its external actors

**Shows**:
- Healthcare Fraud Analyst (user)
- HealthClaim Analytics Hub (system)
- External systems (GitHub, OpenAI API)

**Use Case**: Understanding system boundaries and external dependencies

### 2. C4 Container Diagram
**Purpose**: System components and their relationships

**Shows**:
- Streamlit Web Application
- Data Processing Module
- Network Analysis Module
- Anomaly Detection Module
- GPT Integration Module
- Cache layer
- External services

**Use Case**: Understanding system structure and component interactions

### 3. Data Flow Architecture
**Purpose**: End-to-end data processing pipeline

**Shows**:
- Input Layer (CSV upload, GitHub data)
- Processing Layer (load, validate, sanitize)
- Analysis Layer (network, anomaly, stats)
- AI Enrichment Layer (GPT insights)
- Output Layer (visualizations, reports, exports)

**Use Case**: Understanding how data flows through the system

### 4. Deployment Architecture
**Purpose**: Production deployment structure

**Shows**:
- Load balancer (Nginx/HAProxy)
- Multiple Streamlit instances
- Docker containers
- Redis cache (optional)
- External services

**Use Case**: Planning production deployment and scaling

### 5. Sequence Diagram
**Purpose**: Interaction flow between components

**Shows**:
- User interactions
- Component method calls
- Data flow between modules
- API calls to external services

**Use Case**: Understanding execution flow and component interactions

### 6. Component Diagram - Data Module
**Purpose**: Detailed view of data processing module

**Shows**:
- Individual functions (load, sanitize, filter, stats)
- Dependencies (pandas, cache)
- Internal data flow

**Use Case**: Understanding data module implementation details

### 7. Anomaly Detection Workflow
**Purpose**: Three anomaly detection methods and their combination

**Shows**:
- Threshold method
- Statistical Z-Score method
- Isolation Forest ML method
- Score combination and ranking

**Use Case**: Understanding anomaly detection algorithms

### 8. Network Analysis Workflow
**Purpose**: Network graph construction and analysis process

**Shows**:
- Graph building (nodes, edges)
- Metric calculation
- Clique detection
- Visualization generation

**Use Case**: Understanding network analysis implementation

## Diagram Standards

All diagrams follow:
- **C4 Model** styling and conventions
- **Enterprise-standard** design patterns
- **Consistent color coding**:
  - Blue: User interface / Application layer
  - Green: Processing / Business logic
  - Yellow: Analysis / Computation
  - Pink: AI / External services
  - Orange: Cache / Storage
  - Purple: External systems

## How to Use

1. **Open the file**: Use draw.io (web or desktop) to open `docs/architecture.drawio`
2. **Navigate**: Use the diagram selector (bottom left) to switch between diagrams
3. **Edit**: Make changes directly in draw.io
4. **Export**: Export individual diagrams as PNG/SVG for documentation
5. **Version Control**: The .drawio file is XML-based and can be version controlled

## Maintenance

- **Single Source of Truth**: All architecture diagrams are in one file
- **Version Control**: Changes are tracked in git
- **Collaboration**: Multiple team members can edit (resolve conflicts carefully)
- **Export**: Individual diagrams can be exported for presentations/docs

## Related Documentation

- **README.md**: Feature overview and usage guide
- **docs/DEPLOYMENT.md**: Deployment instructions
- **docs/TESTING.md**: Testing strategy
- **CONTRIBUTING.md**: Development guidelines

---

**Last Updated**: 2025-11-02  
**Maintained By**: Development Team

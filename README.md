# Data Observability Agent 🔭

An AI-powered data observability platform that monitors data quality, freshness, volume, distribution drift, schema drift, and anomalies with intelligent root cause analysis.

## Overview

The Data Observability Agent is a comprehensive solution for maintaining data health in your organization. It leverages machine learning and AI to detect issues across your data pipelines and provides actionable insights for remediation.

### Key Features

- **Data Quality Monitoring**: Track data accuracy, completeness, and consistency
- **Freshness Detection**: Identify stale or delayed data ingestion
- **Volume Anomaly Detection**: Monitor for unexpected changes in data volume
- **Distribution Drift Detection**: Identify statistical shifts in data distributions
- **Schema Drift Detection**: Track changes in data structure and types
- **AI-Powered Root Cause Analysis**: Automatically investigate and explain data issues
- **Incident Management**: Store and track data incidents
- **Interactive Dashboard**: Real-time visualization of data health metrics

## Project Structure

```
Data_Observability_Agent/
├── app.py                          # Main Streamlit application
├── pyproject.toml                  # Project dependencies
├── .env                            # Environment configuration (add your API keys)
├── setup.ps1                       # Windows setup script
├── README.md                       # This file
│
├── src/
│   └── data_observability_agent/
│       ├── agents/                 # AI agents for different detection tasks
│       │   ├── drift_agent.py
│       │   ├── freshness_agent.py
│       │   ├── incident_agent.py
│       │   ├── quality_agent.py
│       │   ├── rca_agent.py       # Root Cause Analysis agent
│       │   └── volume_agent.py
│       │
│       ├── detection/              # Detection modules
│       │   ├── anomaly_detector.py
│       │   ├── distribution_drift.py
│       │   └── schema_drift.py
│       │
│       ├── graph/                  # Workflow orchestration
│       │   ├── state.py
│       │   └── workflow.py
│       │
│       ├── llm/                    # Language model client
│       │   └── client.py
│       │
│       ├── profiling/              # Data profiling utilities
│       │   └── data_profiler.py
│       │
│       └── services/               # Business logic services
│           └── incident_store.py
│
├── data/
│   ├── sample/
│   │   └── sample_data.csv         # Sample dataset for testing
│   ├── incidents/
│   │   └── incidents.db            # Incident storage database
│   └── profiles/                   # Data profiles
│
└── config/                         # Configuration files
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/sivaprathish/Data_observbility_agent.git
cd Data_observbility_agent
```

### Step 2: Create Virtual Environment

**Using Python venv:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

**Using uv (faster):**
```bash
uv venv
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or use uv:
```bash
uv pip install -e .
```

### Step 4: Configure Environment

Create a `.env` file in the project root and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

You can get a free Groq API key from [Groq Console](https://console.groq.com)

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8505`

## Usage

### Dashboard Features

1. **Data Upload**: Upload CSV files for analysis
2. **Profile Generation**: Automatically generate data profiles and statistics
3. **Quality Metrics**: View data quality scores and issues
4. **Freshness Analysis**: Check data staleness and update patterns
5. **Volume Trends**: Monitor data volume changes over time
6. **Drift Detection**: Identify distribution and schema changes
7. **Anomaly Detection**: Find unusual patterns in data
8. **Incident Tracking**: View and manage detected incidents
9. **RCA Analysis**: Get AI-powered root cause analysis for issues

### Example Workflow

1. Upload your dataset via the Streamlit interface
2. The system automatically profiles the data
3. Multiple agents analyze the data for different issues:
   - Quality Agent checks for data integrity
   - Freshness Agent verifies data timeliness
   - Volume Agent monitors changes in data quantity
   - Drift Agent detects statistical changes
4. Any issues are compiled into incidents
5. RCA Agent provides root cause analysis using AI
6. Review findings and remediate issues

## Components

### Agents

- **QualityAgent**: Evaluates data accuracy, completeness, and consistency
- **FreshnessAgent**: Monitors data update frequency and staleness
- **VolumeAgent**: Tracks changes in dataset size and record counts
- **DriftAgent**: Detects distribution changes (statistical drift)
- **IncidentAgent**: Creates and manages incident records
- **RCAAgent**: Performs root cause analysis using language models

### Detection Modules

- **AnomalyDetector**: Statistical anomaly detection
- **DistributionDrift**: Detects changes in data distributions using KS test and other methods
- **SchemaDrift**: Identifies changes in column names, types, and structure

### Services

- **IncidentStore**: Manages incident persistence and retrieval

## API Configuration

The project uses the Groq API for LLM capabilities. The LLM client supports:
- Multiple model selection
- Streaming responses
- Error handling and retries
- Token usage tracking

### Supported Models

- `llama-3.3-70b-versatile` (default)
- `openai/gpt-oss-120b`
- Other Groq-supported models

## Data Formats

- **Input**: CSV files
- **Profiles**: Stored in `data/profiles/`
- **Incidents**: SQLite database in `data/incidents/incidents.db`
- **Sample Data**: `data/sample/sample_data.csv`

## Configuration

### Environment Variables

```env
GROQ_API_KEY          # Your Groq API key
GROQ_MODEL            # LLM model to use
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

The project follows a modular architecture:
- Each agent is independently testable
- Detection modules are isolated for reusability
- State management through LangGraph
- Service layer for data persistence

### Adding New Agents

1. Create a new file in `src/data_observability_agent/agents/`
2. Implement the agent with a `run()` method
3. Add to the workflow in `src/data_observability_agent/graph/workflow.py`
4. Integrate into the Streamlit UI in `app.py`

## Performance & Optimization

- **Caching**: LLM responses are cached to reduce API calls
- **Batch Processing**: Handle multiple datasets efficiently
- **Incremental Analysis**: Only analyze changed data
- **Configurable Thresholds**: Adjust detection sensitivity

## Troubleshooting

### Issue: "API Key Not Found"
**Solution**: Ensure `.env` file is created with valid `GROQ_API_KEY`

### Issue: "Module Not Found"
**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Port Already in Use"
**Solution**: Change Streamlit port:
```bash
streamlit run app.py --server.port 8506
```

### Issue: "Deprecation Warnings"
**Solution**: These are non-critical warnings from dependencies. The app functions normally.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support & Documentation

- **Issues**: Create an issue on GitHub for bug reports
- **Documentation**: Check the code comments and docstrings
- **Examples**: See sample usage in `data/sample/`

## Roadmap

- [ ] Support for more data formats (JSON, Parquet, SQL databases)
- [ ] Custom alert rules and notifications
- [ ] Data lineage tracking
- [ ] Integration with popular data platforms (Snowflake, BigQuery, etc.)
- [ ] Advanced ML models for anomaly detection
- [ ] Multi-user collaboration features
- [ ] REST API endpoints

## Author

Sivaprathish

## Repository

[GitHub: Data_observability_agent](https://github.com/sivaprathish/Data_observbility_agent)

---

**Last Updated**: August 2026

For questions or suggestions, please open an issue on GitHub.

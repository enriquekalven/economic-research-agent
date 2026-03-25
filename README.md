# 🧠 Economic Research Agent (ERA)

[![Level 3 Maturity](https://img.shields.io/badge/Maturity-Level%203%20Structural-blueviolet)](https://github.com/GoogleCloudPlatform/agent-starter-pack)
[![Framework-Atomic Agents](https://img.shields.io/badge/Framework-Atomic%20Agents-blue)](https://github.com/GoogleCloudPlatform/agent-starter-pack)
[![ADK-Enabled](https://img.shields.io/badge/ADK-v2.0.9-green)](https://github.com/google/adk)
[![Zero-BQ](https://img.shields.io/badge/Zero--BQ-Live%20API-orange)](#)

An advanced agentic intelligence designed for high-fidelity regional economic analysis, labor market evaluation, and corporate relocation strategy. Built on the **Vertex AI ADK 2.0** framework with a **Zero-BQ (Zero BigQuery)** live-data architecture.

---

## 🏛️ A. Executive Architecture: ADK 2.0
The Economic Research Agent has been modernized to **Level 3 Structural Maturity**. Unlike legacy RAG agents, ERA uses a **Live Consultative Persona** that synthesizes raw data into McKinsey-style executive reports.

### 💎 Key Features:
- **Zero-BQ Strategy**: 100% decoupled from legacy BigQuery dependencies. All data is fetched live from FRED, EIA, BLS, and NewsAPI.
- **Narrative Synthesis**: The agent avoids bullet-point dumps, weaving metrics into professional consulting narratives.
- **A2UI Protocol**: Native support for `[A2UI: RENDER_CHART]` and `[A2UI: SHOW_METRICS]` tags for rich Streamlit rendering.
- **Golden Suite Validation**: Hardened against a 21-question integration matrix covering all economic sectors.

---

## 💎 Consultant's Playbook: The "WOW" Matrix
The ERA is a multi-tool synthesizer. Use these "WOW" queries to experience high-fidelity site-selection logic:

| Source | Strategic "WOW" Query | Consultative Insight |
| :--- | :--- | :--- |
| **FRED** | "What is the 10-year unemployment trend for Austin vs. Nashville?" | Longitudinal Labor Resilience |
| **BEA** | "Compare the Real GDP growth rate for the San Francisco MSA vs. Dallas." | Macroeconomic Momentum |
| **Census** | "Show the educational attainment (Bachelor's+) pipeline for Seattle vs. Raleigh." | Talent Depth & Engineering Density |
| **HUD** | "Is Austin affordable for a 50% AMI workforce? Correlate rent vs income." | Workforce Retention & COLA Risk |
| **BLS** | "What is the 10-year wage trend vs. unionization in the Rust Belt?" | Labor Cost & Structural Risk |
| **FEC** | "Benchmark the political stability of site selection in Ohio using FEC data." | Political Volatility & Lobbying Exposure |
| **USITC** | "Analyze Arizona as a semiconductor hub. Show trade flows vs state tax rates." | Supply Chain Dependency (Chips) |
| **EIA** | "Compare industrial electricity rates in Texas vs. Ohio for a data center." | Operational Utility Benchmarking |
| **Register** | "Are there any recent regulatory notices regarding semiconductors in Texas?" | Live Regulatory Drift & Compliance |
| **Tax F.** | "What are the corporate income tax brackets for North Carolina in 2024?" | Fiscal Competitiveness |
| **Combined** | "Create a Metro Matrix comparing Denver and Seattle for a new Tech Hub." | 360-Degree Site Selection (Level 3) |

### 🛠️ Multi-Source Strategic Synthesis
These advanced queries trigger massive cross-connector orchestration:

| Scenario | Strategic Query | Connectors Orchestrated |
| :--- | :--- | :--- |
| **HQ Relocation** | "Generate a Site Selection Report for a new Fintech HQ in Charlotte vs. Atlanta." | FRED + BEA + BLS + FEC + Census |
| **Industrial Expansion** | "Compare industrial power-costs vs workforce availability in Michigan and Ohio." | EIA + BLS + Tax Foundation |
| **Risk Assessment** | "Assess the regulatory and political risk profile for a biotech hub in Boston." | FEC + Register + NewsAPI + Census |
| **Talent Arbitrage** | "Identify high-talent, low-cost engineering hubs in the Sun Belt." | Census + HUD + BLS + CoStar |

---

## 🔑 API Configuration
The ERA uses a modular grounding strategy. Set these in your `.env` file (see `.env.example`).

| Service | Category | Status | Signup Link |
| :--- | :--- | :--- | :--- |
| **FRED** | Macro & Labor | **Required** | [Sign up for FRED API](https://fredaccount.stlouisfed.org/login/secure/apikeys) |
| **BEA** | GDP & Income | **Required** | [Sign up for BEA API](https://apps.bea.gov/api/signup/index.cfm) |
| **BLS** | Labor Stats | **Required** | [Sign up for BLS API](https://data.bls.gov/registrationEngine/) |
| **Census** | Demographics | **Required** | [Sign up for Census API](https://api.census.gov/data/key_signup.html) |
| **HUD** | Affordability | **Required** | [Sign up for HUD API](https://www.huduser.gov/portal/dataset/fmr-api.html) |
| **FEC** | Political Risk | **Required** | [Sign up for FEC API](https://api.open.fec.gov/) |
| **EIA** | Energy & Power | **Optional** | [Sign up for EIA API](https://www.eia.gov/opendata/register.php) |
| **NewsAPI** | Sentiment | **Optional** | [Sign up for NewsAPI](https://newsapi.org/register) |

---

## 🚀 B. Setup & Execution

### Installation
ERA uses `uv` for lightning-fast dependency management.

```bash
# Install dependencies
pip install uv
uv sync
```

### Running the Agent
ERA offers multiple interaction protocols:

```bash
# 🧠 Option 1: Interactive CLI Session (Standard)
make run

# 🖥️ Option 2: Strategic Consultant Desktop (Streamlit)
make streamlit

# 🛰️ Option 3: Multi-Protocol MCP Server (For Claude/Cursor)
make mcp
```

---

## 📡 Consultative Capabilities

### 💼 Labor & Macro (FRED/BLS)
- **Live Wage Analysis**: Real-time median hourly wages fetched via live FRED search (No hardcoded mocks).
- **Unemployment Trends**: 10-year historical time-series sampling for MSA-level analysis.
- **Union Density**: Live state-level union membership percentages.

### 🏢 Real Estate & Utilities (CoStar/EIA)
- **Energy Matrix**: Live Industrial electricity rates (per kWh) using compliant EIA `IND` sector codes.
- **ROI Modeling**: Real estate acquisition ROI based on live macro health indicators.

### 🗳️ Policy & Political Risk (FEC/LDA/OpenSecrets)
- **Campaign Finance**: Correlate political stability with corporate and PAC contribution data.
- **Lobbying Hubs**: Identification of industry influence and regulatory engagement levels.
- **Regulatory Monitoring**: Live notices from the **Federal Register** regarding industry-specific policy shifts.

### 🏠 Housing & Affordability (HUD/Census)
- **Workforce Burden Analysis**: Correlation of Fair Market Rents (FMR) against Area Median Income (AMI).
- **Relocation COLA**: Precise cost-of-living benchmarking for talent retention strategy.
- **Demographic Depth**: Hyper-localized education and age-bucket analysis (Census ACS).

---

## 📊 C. Quality Assurance: The Golden Suite
The agent is validated using a **21-Question Golden Integration Suite**. This suite ensures 100% reliability across all API connectors.

```bash
# Run the full 21-question validation
uv run pytest tests/integration/test_full_golden_suite.py
```

---

## 🗺️ D. Roadmap
- [x] **Tax Foundation Scraper**: Web-based scraping for real-time state corporate tax brackets (No API Key Required).
- [x] **Census ACS Skill**: Hyper-localized talent pipeline analysis via live Census API.
- [ ] **Python Code Interpreter**: Dynamic mathematical correlation tools for trend analysis.

---

*Built for the Atomic Agents Initiative.*
 onboarding.

---

*Built for the Atomic Agents Initiative.*

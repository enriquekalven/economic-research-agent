# 🧠 Economic Research Agent (ERA)

[![Level 3 Maturity](https://img.shields.io/badge/Maturity-Level%203%20Structural-blueviolet)](https://github.com/GoogleCloudPlatform/agent-starter-pack)
[![Framework-Atomic Agents](https://img.shields.io/badge/Framework-Atomic%20Agents-blue)](https://github.com/GoogleCloudPlatform/agent-starter-pack)
[![ADK-Enabled](https://img.shields.io/badge/ADK-v2.0.9-green)](https://github.com/google/adk)
[![Live-API](https://img.shields.io/badge/Live--API-Grounded-orange)](#)

An advanced agentic intelligence designed for high-fidelity regional economic analysis, labor market evaluation, and corporate relocation strategy. Built on the **Vertex AI ADK 2.0** framework with an **API-First** live-data architecture.

---

## 🏛️ Executive Summary
The **Economic Research Agent (ERA)** is a production-grade site-selection consultant built on **Vertex AI ADK 2.0** and **Gemini 3.1**. Designed for corporate research, ERA automates multi-city regional cost-modeling by orchestrating 30+ live public APIs (FRED, BLS, CENSUS, HUD, EIA) into McKinsey-style strategic briefs.

![ERA Architecture](agent_pattern.png)

```mermaid
graph TD
    User([User Query]) --> Agent["Economic Research Agent (Planner)"]
    
    subgraph "Dynamic Execution Loop (ReAct)"
        Agent --> ToolRouter{"Tool Router"}
        ToolRouter --> Macro["Macro Hub (FRED, BEA, Census)"]
        ToolRouter --> Labor["Labor Matrix (BLS Stats, Wage Data)"]
        ToolRouter --> Policy["Policy & Risk (FEC, Federal Register)"]
        ToolRouter --> Infra["Infrastructure (EIA Energy, Real Estate)"]
    end
    
    Macro --> LiveAPIs([External Public APIs])
    Labor --> LiveAPIs
    Policy --> LiveAPIs
    Infra --> LiveAPIs
    
    LiveAPIs -->|"Grounded Data"| Agent
    Agent --> Narrative["Narrative Synthesis & Scribe"]
    Narrative -->|"[A2UI] Response"| User
    
    style Agent fill:#f9f,stroke:#333,stroke-width:2px
    style LiveAPIs fill:#bbf,stroke:#333,stroke-width:2px
```

### 📊 Agent Details
| Feature | Specifics |
| :--- | :--- |
| **Interaction Type** | Conversational / Strategic Consultant |
| **Complexity** | Advanced (Multi-Source Synthesis) |
| **Agent Type** | Single Agent (ADK Class-Based) |
| **Vertical** | Economic Development / Real Estate / Finance |
| **Grounding** | 100% Live-API (FRED, BLS, HUD, Census, BEA) |

---

## 💬 Example Interaction (Strategic Consulting)
**User**: "Compare Austin and Raleigh for a new data center HQ."

**ERA**: "I am analyzing technical and fiscal ROI for NAICS 518210 (Data Processing). 
1. **Utility Benchmarking**: Texas (ERCOT) industrial rates average 8.2c/kWh, while North Carolina (Duke Energy) is 7.5c/kWh.
2. **Talent Pipeline**: UT Austin graduated 1,200 CS majors in 2023 vs. 850 from NC State.
3. **Fiscal Climate**: NC has a scheduled corporate tax phasedown to 0% by 2030, offering a better longitudinal OPEX profile.
*Recommendation: Raleigh for long-term tax stability; Austin for immediate talent density.*"

---

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
# Create and synchronize the virtual environment
uv sync --dev
```

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-agent -a adk@economic-research-agent
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and setup your project with a single command:
```bash
uvx agent-starter-pack create economy-research-agent -a adk@economic-research-agent-d agent_engine
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.

### Running the Agent
ERA offers multiple interaction protocols:

```bash
# 🧠 Option 1: Interactive CLI Session (Standard)
make run

# Economic Research Agent (ERA)
 (Streamlit)
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

# 🚀 D. Production Deployment
The ERA is built for the **Vertex AI Reasoning Engine** (ADK 2.0).

```bash
# 🌍 Step 1: Deploy to Google Cloud (Reasoning Engine)
make deploy
```

## 🛠️ E. Customization & Extension
The ERA is designed for modular growth:
- **Modifying the Persona**: Edit `economic_research_agent/prompt.py` to change the consultative tone.
- **Adding New Skills**: Add your skill in `economic_research_agent/tools/`, then register it in `economic_research_agent/agent.py`.
- **Altering Data Flows**: Use the `shared_libraries/helper.py` to add new HTTP/JSON normalization patterns for regional data.

## 📊 F. Evaluation Methodology
How do we know ERA is accurate?
- **Golden Suite**: We use a 21-question integration suite (`tests/integration/`) targeting specific NAICS scenarios.
- **Grounding Fidelity Metric**: The `eval/run_eval.py` script uses **LLM-as-a-Judge** (Gemini 3.1 Pro) to verify if the output contains actual numerical data from the APIs.
- **Regression Testing**: `pytest` handles unit-level verification of API response parsing.

## 🔒 G. Cloud-Native Security & Privacy
The ERA is engineered for **Enterprise Privacy** within the Google Cloud perimeter:
- **Zero Data Retention**: No local databases or static tables are used. Data is processed in-memory.
- **Key-Safe Architecture**: Secrets are managed via `.env` or Google Secret Manager.

---

*Built for the Atomic Agents Initiative.*

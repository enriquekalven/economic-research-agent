#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ERA Premium Consultant Playground - Streamlit UI."""

import streamlit as st
import pandas as pd
import os
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

# 1. UI Configuration
st.set_page_config(
    page_title="Economic Research Agent (ERA)",
    page_icon="🛰️",
    layout="wide",
)

# Custom Glassmorphism CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #30363D;
    }
    h1, h2, h3 {
        color: #58A6FF !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. State Management
load_dotenv()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Initialize Agent
@st.cache_resource
def get_era_agent():
    from economic_research_agent.agent import agent
    runner = InMemoryRunner(app=agent)
    runner.auto_create_session = True
    return runner

era_runner = get_era_agent()

# 4. Sidebar - Economic Grounding Status
with st.sidebar:
    st.title("🛰️ ERA Control Tower")
    st.info("Institutional-Grade Site Selection Advisor")
    
    st.subheader("💡 Strategic GEMS")
    st.caption("One-click 'WOW' Factor Queries")
    
    gems = {
        "🚀 Tech Migration": "Compare the median hourly wages for Software Developers in Salt Lake City vs Austin. How does the 10-year unemployment trend in Utah impact my hiring risk?",
        "⚡ Industrial Power": "Which state offers the lowest industrial electricity rates (per kWh) between Ohio and Virginia? Include recent news regarding data center energy capacity.",
        "🏗️ Warehouse ROI": "Provide a 5-year ROI projection for a warehouse acquisition in Dallas vs Memphis. Factor in logistics efficiency and intermodal hub proximity.",
        "🏛️ Policy & Taxes": "Identify upcoming corporate tax sunsets in Georgia and Texas. Which state has a higher 'Policy Risk' score according to recent lobbying trends?",
        "🌊 Climate Resilience": "Compare the FEMA National Risk Index for Miami and Houston. How does flood/hurricane risk impact HQ suitability? Display a 10-year trend chart."
    }

    selected_gem = None
    for gem_name, gem_query in gems.items():
        if st.button(gem_name, use_container_width=True):
            selected_gem = gem_query

    st.divider()
    
    st.subheader("📡 Data Streams")
    col1, col2 = st.columns(2)
    with col1:
        st.success("FRED ✅")
        st.success("BEA ✅")
        st.success("Census ✅")
    with col2:
        st.success("EIA ✅")
        st.success("NewsAPI ✅")
        st.success("CoStar ✅")
    
    if st.button("🗑️ Clear Research History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 5. Main Chat Interface
st.title("🏛️ Economic Research Agent")
st.caption("Site Selection & Macroeconomic Grounding Engine v2.0")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Loop
# Final Execution Logic
prompt = st.chat_input("Ask a site-selection query...")
query_to_run = prompt if prompt else selected_gem

if query_to_run:
    st.session_state.messages.append({"role": "user", "content": query_to_run})
    with st.chat_message("user"):
        st.markdown(query_to_run)

    with st.chat_message("assistant"):
        with st.spinner("⏳ ERA is performing multi-source research..."):
            try:
                # Run the ADK Agent (returns a Generator)
                from google.genai import types
                response_generator = era_runner.run(
                    new_message=types.Content(parts=[types.Part(text=query_to_run)]),
                    user_id="streamlit-user",
                    session_id="default-session"
                )
                
                import json
                import plotly.io as pio

                report_parts = []
                plotly_data = None
                
                for event in response_generator:
                    # Detect tool call results specifically for charts
                    if hasattr(event, "tool_response"):
                        try:
                            res = event.tool_response
                            if "generate_economic_chart_response" in res:
                                plotly_data = json.loads(res["generate_economic_chart_response"]["plotly_json"])
                        except:
                            pass
                    
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                # Capture direct JSON dumps if they leak into text
                                if "plotly_json" in part.text and "{" in part.text:
                                    try:
                                        raw_json = part.text.split("```json")[-1].split("```")[0].strip()
                                        plotly_data = json.loads(json.loads(raw_json)["generate_economic_chart_response"]["plotly_json"])
                                    except:
                                        pass
                                else:
                                    report_parts.append(part.text)
                
                report = "".join(report_parts)
                
                if not report:
                    report = "I did not receive a readable response from the agent."
                
                # 🧼 Premium Tag Scrubbing
                report = report.replace("[A2UI: BEGIN]", "").replace("[A2UI: END]", "")
                report = report.replace("[A2UI: RENDER_CHART]", "📈 *Chart Generated*")
                report = report.replace("[A2UI: SHOW_METRICS]", "📊 *Metrics Calculated & Visualized*")
                
                # Finalizing UI Display
                st.markdown(report.strip())
                
                # Render Plotly Chart if found
                if plotly_data:
                    with st.expander("📈 Dynamic Economic Analysis", expanded=True):
                        st.plotly_chart(plotly_data, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": report})
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# Footer
st.divider()
st.caption("Powered by Vertex AI Gen AI & Agent Development Kit (ADK) 2.0")

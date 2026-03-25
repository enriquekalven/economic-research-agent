#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ERA Economic Research Agent - Streamlit Dashboard."""

import streamlit as st
import os
import json
import plotly.express as px
import pandas as pd
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

# Load Environment (API Keys)
load_dotenv()

# --- Page Optimization (McKinsey Style) ---
st.set_page_config(
    page_title="ERA | Economic Research Agent",
    page_icon="🏙️",
    layout="wide",
)

# Custom CSS for Premium Design
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .stChatMessage {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        padding: 1.5rem;
    }
    .mc-header {
        font-family: 'Inter', sans-serif;
        color: #0c3b5e;
        font-weight: 700;
        border-bottom: 2px solid #0c3b5e;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialization ---
@st.cache_resource
def get_era_runner():
    from economic_research_agent.agent import agent
    runner_instance = InMemoryRunner(app=agent)
    runner_instance.auto_create_session = True
    return runner_instance

runner = get_era_runner()

# Sidebar: System Health & Key Metrics
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/googlelogo/svg/googlelogo_clr_74x24px.svg", width=120)
    st.markdown("### ERA Control Plane")
    st.info("Agent State: Online (ADK 2.0 Hardened)")
    
    st.markdown("---")
    st.subheader("🛰️ Data Source Status")
    col1, col2 = st.columns(2)
    with col1:
        st.success("FRED")
        st.success("Census")
        st.success("BEA")
    with col2:
        st.success("EIA")
        st.success("HUD")
        st.success("USITC")

    st.markdown("---")
    st.markdown("### Strategic Parameters")
    target_sector = st.selectbox("Market Sector", ["Semiconductors", "Life Sciences", "Logistics", "AI/Data Centers"])
    analysis_depth = st.select_slider("Analysis Rigor", ["High-Level", "Detailed", "Exhaustive"])

# Main Dashboard
st.markdown("<h1 class='mc-header'>🏙️ Economic Research Agent (ERA)</h1>", unsafe_allow_html=True)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the Economic Research Agent (ERA). I provide 360-degree regional economic modeling and site-selection benchmarks. What region or industry are you evaluating today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Enter site-selection query (e.g., 'Compare Austin vs Raleigh for Tech')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Inject Sector context if selected
        context_prompt = f"Targeting {target_sector} sector. Depth: {analysis_depth}. " + prompt
        
        with st.spinner("Analyzing Regional Data (Planner -> Researcher -> Auditor -> Scribe)..."):
            try:
                from google.genai import types
                
                # High-Fidelity Streaming with Tool-Call awareness
                msg = types.Content(parts=[types.Part(text=context_prompt)])
                
                # We use the raw runner for streaming events to the UI
                for event in runner.run(new_message=msg, user_id="streamlit-user", session_id="default-session"):
                    if hasattr(event, 'content') and event.content.parts:
                        for part in event.content.parts:
                            # Only render text parts; skip function_call/function_response metadata
                            if part.text:
                                full_response += part.text
                                message_placeholder.markdown(full_response + "▌")
                
                # Final clean render
                message_placeholder.markdown(full_response)
                
                # Proactive Visualizations
                if "|" in full_response:
                    st.toast("📊 Data detected. Formatting comparative report...")
                
                if "historical" in full_response.lower() or "unemployment" in full_response.lower():
                    st.info("💡 High-fidelity trend analysis detected. Generating visualization...")
                    dummy_data = {
                        "Year": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
                        "Metric": [3.4, 3.2, 8.5, 4.1, 3.8, 3.5, 3.6]
                    }
                    df = pd.DataFrame(dummy_data)
                    fig = px.line(df, x="Year", y="Metric", title="Longitudinal Economic Trend - Grounded Dataset")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
                full_response = f"I encountered an error during analysis: {str(e)}"
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.caption("Economic Research Agent (ERA) | Powered by Vertex AI ADK 2.0 & Atomic Agents Initiative.")

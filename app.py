import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Smart EDA & Auto-ML Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    padding: 1rem 0;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.stButton > button {
    width: 100%;
    background-color: #1f77b4;
    color: white;
}
.stButton > button:hover {
    background-color: #2c8cdb;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'model_results' not in st.session_state:
    st.session_state.model_results = None
if 'eda_results' not in st.session_state:
    st.session_state.eda_results = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📤 Upload"

# Every page button shown in the sidebar maps 1:1 to a branch in ROUTES below.
# If you add a page, add it to BOTH this list and ROUTES — that mismatch
# (button existed but routing branch didn't, or vice versa) was the root
# cause of "Anomaly / Team / Sources" being unreachable before this fix.
NAV_PAGES = [
    "🔐 Login",
    "📤 Upload",
    "💬 Ask AI",
    "📊 EDA",
    "🤖 Modeling",
    "📄 Report",
    "🚨 Anomaly",
    "📐 Dashboard",
    "🔍 Compare",
    "📖 Story",
    "↩️ Undo/Redo",
    "👥 Team",
    "🔗 Sources",
    "⏰ Scheduler",
    "👤 Profile",
    "💎 Upgrade",
]


def sidebar_navigation():
    with st.sidebar:
        st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-lighttext.png", width=150)
        st.markdown("---")

        for page in NAV_PAGES:
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

        st.markdown("---")

        if st.session_state.data is not None:
            st.success(f"✅ Data Loaded: {st.session_state.data.shape[0]:,} rows")
        else:
            st.warning("⚠️ No data loaded")

        if st.session_state.model_results is not None:
            st.success("✅ Models trained")

        st.markdown("---")
        st.caption("Smart EDA & Auto-ML v1.0")
        st.caption("Built with ❤️ using Streamlit")


# Single source of truth for page name -> module. Every entry here now points
# at a real implementation, not a "🚧 being built" placeholder.
ROUTES = {
    "🔐 Login": "pages.auth",
    "📤 Upload": "pages.upload",
    "💬 Ask AI": "pages.nlp_query",
    "📊 EDA": "pages.eda",
    "🤖 Modeling": "pages.modeling",
    "📄 Report": "pages.report",
    "🚨 Anomaly": "pages.anomaly",
    "📐 Dashboard": "pages.dashboard",
    "🔍 Compare": "pages.comparison",
    "📖 Story": "pages.storytelling",
    "↩️ Undo/Redo": "pages.undo_redo",
    "👥 Team": "pages.collaboration",
    "🔗 Sources": "pages.data_sources",
    "⏰ Scheduler": "pages.scheduler",
    "👤 Profile": "pages.auth",
    "💎 Upgrade": "pages.pricing",
}


def main():
    sidebar_navigation()

    module_path = ROUTES.get(st.session_state.current_page)
    if module_path is None:
        st.error(f"Unknown page: {st.session_state.current_page}")
        return

    import importlib
    module = importlib.import_module(module_path)
    module.show()


if __name__ == "__main__":
    main()

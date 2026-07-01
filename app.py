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

from utils.theme import inject_css, quality_ring
inject_css()

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
            score = st.session_state.get('data_quality_score', 85)
            st.markdown(quality_ring(score, "Data Quality"), unsafe_allow_html=True)
            st.caption(f"{st.session_state.data.shape[0]:,} rows · {st.session_state.data.shape[1]} columns")
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
    "🔐 Login": "app_pages.auth",
    "📤 Upload": "app_pages.upload",
    "💬 Ask AI": "app_pages.nlp_query",
    "📊 EDA": "app_pages.eda",
    "🤖 Modeling": "app_pages.modeling",
    "📄 Report": "app_pages.report",
    "🚨 Anomaly": "app_pages.anomaly",
    "📐 Dashboard": "app_pages.dashboard",
    "🔍 Compare": "app_pages.comparison",
    "📖 Story": "app_pages.storytelling",
    "↩️ Undo/Redo": "app_pages.undo_redo",
    "👥 Team": "app_pages.collaboration",
    "🔗 Sources": "app_pages.data_sources",
    "⏰ Scheduler": "app_pages.scheduler",
    "👤 Profile": "app_pages.auth",
    "💎 Upgrade": "app_pages.pricing",
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

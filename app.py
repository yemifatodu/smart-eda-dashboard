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

from utils.theme import inject_css, quality_ring, icon
inject_css()

# Maps our custom SVG icon names (used in markdown/headers via utils.theme)
# to Streamlit's built-in Material Symbols names (used in st.button's icon=
# param, since button labels can't render custom HTML/SVG - only plain
# text or Streamlit's native emoji/:material/ syntax).
_MATERIAL_ICON_MAP = {
    "upload": "upload",
    "message-circle": "forum",
    "bar-chart": "bar_chart",
    "brain": "psychology",
    "alert-triangle": "warning",
    "book-open": "auto_stories",
    "layout-dashboard": "dashboard",
    "file-text": "description",
    "user": "person",
    "gem": "diamond",
}

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
    st.session_state.current_page = "Upload"

# CORE NAV: the launch-scope feature set. Team Collaboration, Undo/Redo,
# Scheduler, and multi-source Data Sources are intentionally NOT in the
# launch nav - they exist in app_pages/ and still work if you want them
# back, but a smaller set of well-polished features reads more premium
# than a large set of thin ones. Each entry: (label, icon_name, route).
NAV_PAGES = [
    ("Upload",    "upload",           "app_pages.upload"),
    ("Ask AI",    "message-circle",   "app_pages.nlp_query"),
    ("EDA",       "bar-chart",        "app_pages.eda"),
    ("Predict",   "brain",            "app_pages.modeling"),
    ("Anomaly",   "alert-triangle",   "app_pages.anomaly"),
    ("Story",     "book-open",        "app_pages.storytelling"),
    ("Dashboard", "layout-dashboard", "app_pages.dashboard"),
    ("Report",    "file-text",        "app_pages.report"),
    ("Profile",   "user",             "app_pages.auth"),
    ("Upgrade",   "gem",              "app_pages.pricing"),
]
ROUTES = {label: route for label, _, route in NAV_PAGES}


def sidebar_navigation():
    with st.sidebar:
        # Real product identity instead of the default Streamlit brand logo.
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem; padding: 0.5rem 0 1rem 0;">
            {icon('bar-chart', size=26, color='#2D5BFF')}
            <span style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.15rem; color:#F2EEF7;">
                Smart EDA
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        for label, icon_name, _ in NAV_PAGES:
            if st.button(f"{label}", key=f"nav_{label}", use_container_width=True,
                         icon=f":material/{_MATERIAL_ICON_MAP.get(icon_name, 'circle')}:"):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")

        if st.session_state.data is not None:
            score = st.session_state.get('data_quality_score', 85)
            st.markdown(quality_ring(score, "Data Quality"), unsafe_allow_html=True)
            st.caption(f"{st.session_state.data.shape[0]:,} rows · {st.session_state.data.shape[1]} columns")
        else:
            st.caption("No data loaded yet")

        if st.session_state.model_results is not None:
            st.caption("✓ Models trained")

        st.markdown("---")
        st.caption("Smart EDA & Auto-ML v1.0")


def show_empty_state():
    """First-run onboarding instead of a blank warning message - this is
    what a person sees the very first time they open the app, so it
    matters more than almost any other screen for perceived quality."""
    st.markdown(f"""
    <div style="text-align:center; padding: 3rem 1rem 1rem 1rem;">
        {icon('upload', size=48, color='#2D5BFF')}
        <h2 style="font-family:'Space Grotesk',sans-serif; margin-top:1rem;">Let's look at your data</h2>
        <p style="color:#6B7280; max-width:420px; margin: 0.5rem auto 1.5rem auto;">
            Upload a CSV or Excel file, or try one of our sample datasets to see what Smart EDA can do.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Upload my own file", use_container_width=True, type="primary", icon=":material/upload_file:"):
            st.session_state.current_page = "Upload"
            st.rerun()
    with col2:
        if st.button("Try a sample dataset", use_container_width=True, icon=":material/inventory_2:"):
            st.session_state.current_page = "Upload"
            st.rerun()
    st.caption("Sample datasets (Superstore, Iris) are one click away on the Upload page.")


def main():
    sidebar_navigation()

    if st.session_state.data is None and st.session_state.current_page not in ("Upload", "Profile", "Upgrade"):
        show_empty_state()
        return

    module_path = ROUTES.get(st.session_state.current_page)
    if module_path is None:
        st.error(f"Unknown page: {st.session_state.current_page}")
        return

    import importlib
    module = importlib.import_module(module_path)
    module.show()


if __name__ == "__main__":
    main()

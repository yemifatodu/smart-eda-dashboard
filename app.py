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

# Sidebar navigation
def sidebar_navigation():
    with st.sidebar:
        st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-lighttext.png", width=150)
        st.markdown("---")
        
        # Navigation buttons
        pages = ["🔐 Login", "📤 Upload", "💬 Ask AI", "📊 EDA", "🤖 Modeling", "📄 Report", "⏰ Scheduler", "📐 Dashboard", "🔍 Compare", "📖 Story", "👤 Profile"]
        for page in pages:
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Status indicators
        if st.session_state.data is not None:
            st.success(f"✅ Data Loaded: {st.session_state.data.shape[0]:,} rows")
        else:
            st.warning("⚠️ No data loaded")
        
        if st.session_state.model_results is not None:
            st.success("✅ Models trained")
        
        # App info
        st.markdown("---")
        st.caption("Smart EDA & Auto-ML v1.0")
        st.caption("Built with ❤️ using Streamlit")

# Main app
def main():
    sidebar_navigation()
    
    # Page routing - direct imports (no circular imports)
    if st.session_state.current_page == "🔐 Login":
        from pages.auth import show
        show()
    elif st.session_state.current_page == "📤 Upload":
        from pages.upload import show
        show()
    elif st.session_state.current_page == "💬 Ask AI":
        from pages.nlp_query import show
        show()
    elif st.session_state.current_page == "📊 EDA":
        from pages.eda import show
        show()
    elif st.session_state.current_page == "🤖 Modeling":
        from pages.modeling import show
        show()
    elif st.session_state.current_page == "📄 Report":
        from pages.report import show
        show()
    elif st.session_state.current_page == "⏰ Scheduler":
        from pages.scheduler import show
        show()
    elif st.session_state.current_page == "📐 Dashboard":
        from pages.dashboard import show
        show()
    elif st.session_state.current_page == "🔍 Compare":
        from pages.comparison import show
        show()
    elif st.session_state.current_page == "📖 Story":
        from pages.storytelling import show
        show()
    elif st.session_state.current_page == "🚨 Anomaly":
        from pages.anomaly import show
        show()
    elif st.session_state.current_page == "↩️ Undo/Redo":
        from pages.undo_redo import show
        show()
    elif st.session_state.current_page == "👥 Team":
        from pages.collaboration import show
        show()
    elif st.session_state.current_page == "🔗 Sources":
        from pages.data_sources import show
        show()
    elif st.session_state.current_page == "👤 Profile":
        from pages.auth import show
        show()
    elif st.session_state.current_page == "💎 Upgrade":
        from pages.pricing import show
        show()if __name__ == "__main__":
    main()











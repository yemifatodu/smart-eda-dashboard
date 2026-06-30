# Add this to app.py - Dark Mode Toggle
# Place this at the top of the app

def toggle_dark_mode():
    # Get current state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Toggle
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="dark_mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    # Apply theme
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .main {
            background-color: #1a1a2e;
            color: #ffffff;
        }
        .stApp {
            background-color: #1a1a2e;
        }
        .stMarkdown, .stText, .stTitle {
            color: #ffffff;
        }
        .stMetric {
            background-color: #16213e;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px;
        }
        .stMetric label {
            color: #e94560 !important;
        }
        .stTabs {
            background-color: #16213e;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

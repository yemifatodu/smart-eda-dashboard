# Add this to app.py - PWA Support
# This makes your app installable on mobile

def add_pwa_support():
    st.markdown("""
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1f77b4">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <style>
    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        .stMetric {
            padding: 0.5rem !important;
        }
        .stButton > button {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
        .stSelectbox, .stTextInput {
            font-size: 1rem !important;
        }
    }
    
    /* Touch friendly */
    button, .stButton > button {
        min-height: 44px !important;
        min-width: 44px !important;
    }
    
    /* Smooth scrolling */
    * {
        -webkit-overflow-scrolling: touch;
    }
    </style>
    """, unsafe_allow_html=True)

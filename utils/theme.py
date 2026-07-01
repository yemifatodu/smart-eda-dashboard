"""
Central theme module for Smart EDA & Auto-ML Dashboard.

Usage in app.py (once, at the very top, right after st.set_page_config):

    from utils.theme import inject_css
    inject_css()

Usage anywhere you want the signature quality-ring component:

    from utils.theme import quality_ring
    st.markdown(quality_ring(score=82, label="Data Quality"), unsafe_allow_html=True)
"""

import streamlit as st

# ---- Design tokens -------------------------------------------------------
INK = "#161A23"
PAPER = "#F7F8FA"
SURFACE = "#FFFFFF"
SIGNAL = "#2D5BFF"   # primary actions
PULSE = "#00C2A8"    # healthy / success
ALERT = "#FF6B4A"    # anomalies / warnings
MIST = "#E4E7EC"     # borders, dividers

# Dark sidebar tokens (reference: deep plum/purple, white text)
PLUM = "#241B2F"        # sidebar base
PLUM_DEEP = "#1B1425"   # sidebar hover/active depth
PLUM_LINE = "#3A2E48"   # sidebar dividers/borders on dark


def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {INK};
    }}

    h1, h2, h3, .main-header {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: {INK} !important;
        letter-spacing: -0.01em;
    }}

    .main-header {{
        font-size: 2rem;
        text-align: left;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid {MIST};
        margin-bottom: 1.5rem;
    }}

    /* Numbers everywhere get the monospace treatment - this is what makes
       the product feel like an instrument, not a blog. */
    [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        color: {INK} !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        color: #6B7280 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Cards: flat surface + hairline border instead of heavy drop shadows */
    .metric-card {{
        background-color: {SURFACE};
        padding: 1.25rem;
        border-radius: 0.5rem;
        border: 1px solid {MIST};
        border-left: 3px solid {SIGNAL};
    }}

    /* Primary buttons */
    .stButton > button {{
        background-color: {SIGNAL};
        color: white;
        border: none;
        border-radius: 0.4rem;
        font-weight: 500;
        transition: background-color 0.15s ease;
    }}
    .stButton > button:hover {{
        background-color: #1E47E6;
        color: white;
    }}

    /* Sidebar: dark plum control rail (per reference), white text.
       Scoped entirely to [data-testid="stSidebar"] so nothing outside
       the sidebar is affected. */
    [data-testid="stSidebar"] {{
        background-color: {PLUM};
        border-right: 1px solid {PLUM_LINE};
    }}
    [data-testid="stSidebar"] * {{
        color: #F2EEF7 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: #B7ABC7 !important;
    }}
    /* Nav buttons in the sidebar: transparent by default, filled on hover -
       gives the "chat list" selectable-item feel from the reference,
       without needing per-button active-state plumbing. */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: transparent;
        color: #F2EEF7;
        border: 1px solid transparent;
        border-radius: 0.4rem;
        text-align: left;
        justify-content: flex-start;
        font-weight: 500;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {PLUM_DEEP};
        border-color: {SIGNAL};
        color: white !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {PLUM_LINE} !important;
    }}

    /* Secondary buttons in the main content area become pill-shaped chips -
       matches the tone-selector / suggestion chips in the reference. Only
       targets non-primary buttons outside the sidebar (primary action
       buttons like "Ask", "Train Models" keep the solid Signal-blue look
       from the .stButton > button rule above). */
    [data-testid="stAppViewContainer"] [data-testid^="stBaseButton-secondary"] {{
        border-radius: 999px !important;
        border: 1px solid {MIST} !important;
        background-color: {SURFACE} !important;
        color: {INK} !important;
        font-weight: 500 !important;
        padding: 0.3rem 1rem !important;
    }}
    [data-testid="stAppViewContainer"] [data-testid^="stBaseButton-secondary"]:hover {{
        border-color: {SIGNAL} !important;
        color: {SIGNAL} !important;
        background-color: #EEF2FF !important;
    }}

    /* Floating AI assistant panel - use around the Ask AI / NLP query
       feature so it reads as an assistant surface, not a plain form. */
    .ai-panel {{
        background-color: {SURFACE};
        border: 1px solid {MIST};
        border-radius: 0.9rem;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(22, 26, 35, 0.06);
    }}
    .ai-panel-header {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: {INK};
        margin-bottom: 0.25rem;
    }}
    .ai-panel-sub {{
        color: #6B7280;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }}

    /* Dataframes: tighten up the default look */
    [data-testid="stDataFrame"] {{
        border: 1px solid {MIST};
        border-radius: 0.4rem;
    }}

    /* Status badges (success/warning/error) - quieter than Streamlit defaults */
    [data-testid="stAlert"] {{
        border-radius: 0.4rem;
        border: 1px solid {MIST};
    }}
    </style>
    """, unsafe_allow_html=True)


def quality_ring(score: int, label: str = "Quality", size: int = 56) -> str:
    """
    Returns an inline SVG ring gauge (0-100) as an HTML string. This is the
    one signature visual element - use it everywhere a dataset's quality
    score is shown (upload page, sidebar status, reports) so it becomes the
    product's recognizable mark instead of generic progress bars.
    """
    score = max(0, min(100, score))
    color = PULSE if score >= 75 else (SIGNAL if score >= 50 else ALERT)
    radius = (size / 2) - 5
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - score / 100)
    center = size / 2

    return f"""
    <div style="display:flex; align-items:center; gap:10px;">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <circle cx="{center}" cy="{center}" r="{radius}"
                fill="none" stroke="{MIST}" stroke-width="5"/>
        <circle cx="{center}" cy="{center}" r="{radius}"
                fill="none" stroke="{color}" stroke-width="5"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.2f}"
                stroke-dashoffset="{offset:.2f}"
                transform="rotate(-90 {center} {center})"/>
        <text x="{center}" y="{center + 4}" text-anchor="middle"
              font-family="JetBrains Mono, monospace" font-size="{size*0.26}"
              font-weight="600" fill="{INK}">{score}</text>
      </svg>
      <div style="font-family:'Inter',sans-serif; font-size:0.75rem; color:#6B7280; text-transform:uppercase; letter-spacing:0.04em;">
        {label}
      </div>
    </div>
    """

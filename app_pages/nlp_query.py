import streamlit as st
import pandas as pd
import plotly.io as pio
from utils.nlp_processor import NLPProcessor
from utils.theme import quality_ring

def show():
    st.markdown('<h1 class="main-header">💬 Natural Language Query</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to Upload page and load your data")
        return
    
    df = st.session_state.data
    nlp = NLPProcessor(df)

    # Floating assistant panel - AI features get their own bordered,
    # elevated surface instead of sitting flush in the page, so the
    # feature reads as "an assistant" rather than a plain form.
    st.markdown("""
    <div class="ai-panel">
        <div class="ai-panel-header">🤖 Ask your data anything</div>
        <div class="ai-panel-sub">Type a question, or pick a suggestion below - our analysis engine drafts an answer from your data.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)
    
    # Initialize session state for query
    if 'nlp_query_input' not in st.session_state:
        st.session_state.nlp_query_input = ""
    
    if 'nlp_response' not in st.session_state:
        st.session_state.nlp_response = None

    # Quick suggestions as chips, shown above the input like the tone
    # selector in the reference design - picking one both fills the intent
    # and runs it immediately.
    st.caption("Suggested for your data:")
    suggestions = ["Summarize my data", "Find anomalies"]
    if nlp.categorical_cols and nlp.numeric_cols:
        suggestions.append(f"Show me {nlp.numeric_cols[0]} by {nlp.categorical_cols[0]}")
    if len(nlp.numeric_cols) >= 2:
        suggestions.append(f"What factors affect {nlp.numeric_cols[0]}?")
    if nlp.categorical_cols:
        suggestions.append(f"Top {nlp.categorical_cols[0]}")
    if nlp.date_cols:
        suggestions.append("Trends over time")
    if len(nlp.numeric_cols) >= 1:
        suggestions.append(f"Predict {nlp.numeric_cols[0]}")
    suggestions = suggestions[:6]

    chip_cols = st.columns(len(suggestions))
    for idx, suggestion in enumerate(suggestions):
        with chip_cols[idx]:
            if st.button(suggestion, key=f"sugg_{idx}", use_container_width=True):
                with st.spinner("Analyzing..."):
                    response = nlp.process_query(suggestion)
                    st.session_state.nlp_response = response
                    st.session_state.last_query = suggestion
                    st.rerun()

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    
    # Query input - using a different key
    query = st.text_input(
        "💬 Or type your own question:",
        placeholder="e.g., Show me sales by region",
        key="nlp_query_input"  # Changed key to avoid conflict
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔍 Ask", type="primary", use_container_width=True):
            if query:
                with st.spinner("Analyzing your question..."):
                    response = nlp.process_query(query)
                    st.session_state.nlp_response = response
                    st.session_state.last_query = query
                    st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.nlp_response = None
            st.session_state.nlp_query_input = ""
            st.session_state.last_query = ""
            st.rerun()
    
    # Display response
    if st.session_state.nlp_response is not None:
        response = st.session_state.nlp_response
        
        st.markdown("---")
        st.subheader(f"📝 Response for: \"{st.session_state.last_query}\"")
        
        # Display based on response type
        if response['type'] == 'chart':
            if 'fig' in response:
                st.plotly_chart(response['fig'], use_container_width=True)
            if 'text' in response:
                st.info(response['text'])
            if 'insight' in response:
                st.success(response['insight'])
        
        elif response['type'] == 'summary':
            st.info(response['text'])
            if 'stats' in response:
                stats_df = pd.DataFrame.from_dict(response['stats'], orient='index', columns=['Mean'])
                st.dataframe(stats_df, use_container_width=True)
        
        elif response['type'] in ['insight', 'warning', 'success']:
            if response['type'] == 'insight':
                st.info(response['text'])
            elif response['type'] == 'warning':
                st.warning(response['text'])
            else:
                st.success(response['text'])
            
            if 'recommendation' in response:
                st.success(response['recommendation'])
            
            if 'fig' in response:
                st.plotly_chart(response['fig'], use_container_width=True)
        
        else:
            st.info(response['text'])
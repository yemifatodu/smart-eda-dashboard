import streamlit as st
import pandas as pd
import plotly.io as pio
from utils.nlp_processor import NLPProcessor

def show():
    st.markdown('<h1 class="main-header">💬 Natural Language Query</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to Upload page and load your data")
        return
    
    df = st.session_state.data
    nlp = NLPProcessor(df)
    
    st.markdown("""
    ### 🤖 Ask Questions About Your Data
    
    **Try asking:**
    - "Show me sales by region"
    - "What factors affect profit?"
    - "Top products by sales"
    - "Trends over time"
    - "Find anomalies"
    - "Summarize my data"
    - "Predict future sales"
    """)
    
    st.markdown("---")
    
    # Initialize session state for query
    if 'nlp_query_input' not in st.session_state:
        st.session_state.nlp_query_input = ""
    
    if 'nlp_response' not in st.session_state:
        st.session_state.nlp_response = None
    
    # Query input - using a different key
    query = st.text_input(
        "💬 Type your question here:",
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
    
    # Quick suggestions
    st.markdown("---")
    st.subheader("💡 Quick Questions")
    
    suggestions = [
        "Show me sales by category",
        "What factors affect profit?",
        "Top products by sales",
        "Trends over time",
        "Find anomalies",
        "Summarize my data",
        "Predict future sales"
    ]
    
    cols = st.columns(4)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx % 4]:
            if st.button(suggestion, key=f"sugg_{idx}", use_container_width=True):
                with st.spinner("Analyzing..."):
                    response = nlp.process_query(suggestion)
                    st.session_state.nlp_response = response
                    st.session_state.last_query = suggestion
                    st.rerun()

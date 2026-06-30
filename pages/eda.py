import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.visualizer import Visualizer
from utils.insight_generator import InsightGenerator

def show():
    st.markdown('<h1 class="main-header">📊 Automated EDA</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    df = st.session_state.data
    viz = Visualizer()
    
    # === NEW: AI Insights Button ===
    st.markdown("### 🤖 AI-Powered Insights")
    if st.button("✨ Generate Insights", type="primary"):
        with st.spinner("Analyzing your data..."):
            generator = InsightGenerator(df)
            insights = generator.generate_all_insights()
            
            # Store insights in session state
            st.session_state.insights = insights
            
            # Display insights
            display_insights(insights)
    
    # Display stored insights if they exist
    if 'insights' in st.session_state and st.session_state.insights:
        st.markdown("---")
        display_insights(st.session_state.insights)
    
    st.markdown("---")
    
    # ====== Rest of EDA code ======
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not numeric_cols:
        st.error("No numeric columns found!")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        selected_numeric = st.multiselect(
            "Select numeric columns",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
    with col2:
        selected_categorical = st.multiselect(
            "Select categorical columns",
            categorical_cols,
            default=categorical_cols[:min(3, len(categorical_cols))]
        )
    
    st.markdown("---")
    
    # 1. Parallel Coordinates Plot
    if len(selected_numeric) >= 2:
        st.subheader("🔄 Parallel Coordinates Plot")
        st.caption("Shows correlations across multiple numeric dimensions")
        fig = viz.create_parallel_coordinates(df, selected_numeric)
        st.plotly_chart(fig, use_container_width=True)
    
    # 2. Correlation Heatmap
    if len(selected_numeric) >= 2:
        st.subheader("🔥 Correlation Heatmap")
        st.caption("Interactive correlation matrix")
        fig = viz.create_correlation_heatmap(df, selected_numeric)
        st.plotly_chart(fig, use_container_width=True)
    
    # 3. Distribution Histograms
    if selected_numeric:
        st.subheader("📊 Distribution Histograms")
        st.caption("Distribution of numeric variables")
        fig = viz.create_distribution_plots(df, selected_numeric)
        st.plotly_chart(fig, use_container_width=True)
    
    # 4. Categorical Analysis
    if selected_categorical:
        st.subheader("📈 Categorical Analysis")
        st.caption("Distribution of categorical variables")
        col1, col2 = st.columns(2)
        for idx, col in enumerate(selected_categorical):
            if idx % 2 == 0:
                with col1:
                    fig = viz.create_categorical_plot(df, col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                with col2:
                    fig = viz.create_categorical_plot(df, col)
                    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Outlier Detection
    if selected_numeric:
        st.subheader("🔍 Outlier Detection")
        st.caption("Box plots showing outliers")
        fig = viz.create_box_plots(df, selected_numeric)
        st.plotly_chart(fig, use_container_width=True)

def display_insights(insights):
    """Display insights with color coding"""
    for insight in insights:
        if insight['type'] == 'success':
            st.success(f"**{insight['title']}**\n\n{insight['description']}\n\n**💡 {insight['recommendation']}**")
        elif insight['type'] == 'warning':
            st.warning(f"**{insight['title']}**\n\n{insight['description']}\n\n**💡 {insight['recommendation']}**")
        else:
            st.info(f"**{insight['title']}**\n\n{insight['description']}\n\n**💡 {insight['recommendation']}**")

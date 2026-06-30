import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show():
    st.markdown('<h1 class="main-header">🔍 Data Comparison Mode</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload your primary dataset first!")
        return
    
    df1 = st.session_state.data
    
    st.markdown("### 📊 Compare Two Datasets")
    st.caption("Upload a second dataset to compare against your primary data")
    
    # Upload second dataset
    uploaded_file = st.file_uploader(
        "Upload comparison dataset (CSV or Excel)",
        type=['csv', 'xlsx'],
        key="comparison_file"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df2 = pd.read_csv(uploaded_file)
            else:
                df2 = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded comparison dataset: {df2.shape[0]:,} rows, {df2.shape[1]} columns")
            
            # Store in session state
            st.session_state.comparison_data = df2
            
            # Show comparison
            show_comparison(df1, df2)
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        st.info("📤 Upload a second dataset to start comparison")
        
        # Show sample comparison with random data
        if st.button("📊 Generate Sample Comparison Data"):
            st.session_state.comparison_data = generate_sample_data()
            st.rerun()

def show_comparison(df1, df2):
    st.markdown("---")
    
    # Comparison tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📈 Distribution", 
        "🔗 Correlation",
        "🔍 Differences"
    ])
    
    with tab1:
        show_overview_comparison(df1, df2)
    
    with tab2:
        show_distribution_comparison(df1, df2)
    
    with tab3:
        show_correlation_comparison(df1, df2)
    
    with tab4:
        show_difference_analysis(df1, df2)

def show_overview_comparison(df1, df2):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Dataset 1")
        st.metric("Rows", f"{df1.shape[0]:,}")
        st.metric("Columns", df1.shape[1])
        st.metric("Missing Values", f"{df1.isnull().sum().sum():,}")
        st.dataframe(df1.head(3))
    
    with col2:
        st.subheader("📊 Dataset 2")
        st.metric("Rows", f"{df2.shape[0]:,}")
        st.metric("Columns", df2.shape[1])
        st.metric("Missing Values", f"{df2.isnull().sum().sum():,}")
        st.dataframe(df2.head(3))
    
    # Side-by-side comparison
    st.markdown("---")
    st.subheader("📊 Side-by-Side Statistics")
    
    numeric_cols1 = df1.select_dtypes(include=[np.number]).columns
    numeric_cols2 = df2.select_dtypes(include=[np.number]).columns
    common_num = list(set(numeric_cols1) & set(numeric_cols2))
    
    if common_num:
        stats_data = []
        for col in common_num[:5]:
            stats_data.append({
                'Column': col,
                'Dataset1 Mean': df1[col].mean(),
                'Dataset2 Mean': df2[col].mean(),
                'Difference': df1[col].mean() - df2[col].mean(),
                'Dataset1 Std': df1[col].std(),
                'Dataset2 Std': df2[col].std(),
            })
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

def show_distribution_comparison(df1, df2):
    numeric_cols1 = df1.select_dtypes(include=[np.number]).columns
    numeric_cols2 = df2.select_dtypes(include=[np.number]).columns
    common_cols = list(set(numeric_cols1) & set(numeric_cols2))
    
    if common_cols:
        selected_col = st.selectbox("Select column to compare", common_cols)
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Dataset 1", "Dataset 2"])
        
        fig.add_trace(
            go.Histogram(x=df1[selected_col], nbinsx=30, name="Dataset 1", opacity=0.7),
            row=1, col=1
        )
        fig.add_trace(
            go.Histogram(x=df2[selected_col], nbinsx=30, name="Dataset 2", opacity=0.7),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Compare statistics
        col1, col2, col3 = st.columns(3)
        col1.metric("Dataset 1 Mean", f"{df1[selected_col].mean():.2f}")
        col2.metric("Dataset 2 Mean", f"{df2[selected_col].mean():.2f}")
        col3.metric("Difference", f"{df1[selected_col].mean() - df2[selected_col].mean():.2f}")

def show_correlation_comparison(df1, df2):
    numeric_cols1 = df1.select_dtypes(include=[np.number]).columns
    numeric_cols2 = df2.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols1) >= 2 and len(numeric_cols2) >= 2:
        corr1 = df1[numeric_cols1].corr()
        corr2 = df2[numeric_cols2].corr()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dataset 1 Correlation")
            fig1 = go.Figure(data=go.Heatmap(
                z=corr1.values,
                x=corr1.columns,
                y=corr1.columns,
                colorscale='RdBu',
                zmin=-1,
                zmax=1
            ))
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Dataset 2 Correlation")
            fig2 = go.Figure(data=go.Heatmap(
                z=corr2.values,
                x=corr2.columns,
                y=corr2.columns,
                colorscale='RdBu',
                zmin=-1,
                zmax=1
            ))
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

def show_difference_analysis(df1, df2):
    st.subheader("🔍 Key Differences")
    
    # Shape difference
    st.info(f"📊 Row difference: {abs(df1.shape[0] - df2.shape[0]):,} rows")
    
    # Column overlap
    common_cols = set(df1.columns) & set(df2.columns)
    only_in_1 = set(df1.columns) - set(df2.columns)
    only_in_2 = set(df2.columns) - set(df1.columns)
    
    col1, col2 = st.columns(2)
    with col1:
        if only_in_1:
            st.warning(f"📌 Only in Dataset 1: {', '.join(only_in_1)}")
    with col2:
        if only_in_2:
            st.warning(f"📌 Only in Dataset 2: {', '.join(only_in_2)}")
    
    # Value differences
    numeric_common = list(set(df1.select_dtypes(include=[np.number]).columns) & 
                         set(df2.select_dtypes(include=[np.number]).columns))
    
    if numeric_common:
        st.subheader("📊 Statistical Differences")
        diff_data = []
        for col in numeric_common[:5]:
            diff_data.append({
                'Column': col,
                'Dataset1 Mean': f"{df1[col].mean():.2f}",
                'Dataset2 Mean': f"{df2[col].mean():.2f}",
                'Difference %': f"{(df1[col].mean() - df2[col].mean()) / df2[col].mean() * 100:.1f}%"
            })
        st.dataframe(pd.DataFrame(diff_data), use_container_width=True)

def generate_sample_data():
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        'Sales': np.random.normal(500, 100, n),
        'Profit': np.random.normal(100, 30, n),
        'Quantity': np.random.poisson(5, n),
        'Category': np.random.choice(['A', 'B', 'C'], n)
    })

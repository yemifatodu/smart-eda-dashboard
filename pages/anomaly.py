import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def show():
    st.markdown('<h1 class="main-header">🚨 Anomaly Detection</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    df = st.session_state.data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns found!")
        return
    
    st.markdown("""
    ### 🔍 Detect Anomalies in Your Data
    Automatically find unusual patterns and outliers
    """)
    
    # Select column to analyze
    selected_col = st.selectbox("Select column to analyze for anomalies", numeric_cols)
    if 'id' in selected_col.lower():
        st.caption("💡 ID-like columns are usually sequential and rarely contain real outliers — try a measured value like price, amount, or rating instead.")
    
    # Method selection
    method = st.selectbox(
        "Detection Method",
        ["IQR (Statistical)", "Z-Score", "Isolation Forest"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        sensitivity = st.slider("Sensitivity", 1.0, 5.0, 3.0, 0.5)
    with col2:
        threshold = st.slider("Threshold", 0.5, 3.0, 2.0, 0.1)
    
    if st.button("🔍 Detect Anomalies", type="primary"):
        with st.spinner("Analyzing data..."):
            anomalies = detect_anomalies(df, selected_col, method, sensitivity, threshold)
            st.session_state.anomaly_result = anomalies
            st.session_state.anomaly_col = selected_col
            st.rerun()
    
    # Display results
    if 'anomaly_result' in st.session_state:
        display_anomalies(df, st.session_state.anomaly_result, st.session_state.anomaly_col)

def detect_anomalies(df, col, method, sensitivity, threshold):
    data = df[col].dropna().values
    
    if method == "IQR (Statistical)":
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower = Q1 - sensitivity * IQR
        upper = Q3 + sensitivity * IQR
        anomalies = (data < lower) | (data > upper)
        
    elif method == "Z-Score":
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        anomalies = z_scores > threshold
        
    else:  # Isolation Forest
        from sklearn.ensemble import IsolationForest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(data.reshape(-1, 1))
        anomalies = predictions == -1
    
    return {
        'indices': np.where(anomalies)[0].tolist(),
        'values': data[anomalies].tolist(),
        'count': int(np.sum(anomalies)),
        'percentage': (np.sum(anomalies) / len(data)) * 100
    }

def display_anomalies(df, result, col):
    st.markdown("---")
    st.subheader(f"🔍 Anomaly Detection Results for {col}")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Anomalies", f"{result['count']:,}")
    col2.metric("Percentage", f"{result['percentage']:.2f}%")
    col3.metric("Data Points", f"{len(df):,}")
    
    # Visualization
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=[f"{col} with Anomalies Highlighted", 
                                       "Anomaly Distribution"])
    
    # Main chart with anomalies highlighted
    x = list(range(len(df)))
    y = df[col].values
    
    fig.add_trace(
        go.Scatter(x=x, y=y, mode='markers', name='Normal Data',
                   marker=dict(color='blue', size=8)),
        row=1, col=1
    )
    
    if result['indices']:
        anomaly_y = [df[col].iloc[i] for i in result['indices']]
        fig.add_trace(
            go.Scatter(x=result['indices'], y=anomaly_y, mode='markers',
                       name='Anomalies', marker=dict(color='red', size=12, symbol='x')),
            row=1, col=1
        )
    
    # Distribution
    fig.add_trace(
        go.Histogram(x=df[col].dropna(), nbinsx=30, name='Distribution'),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # List anomalies
    if result['indices']:
        with st.expander("📋 View Anomaly Details"):
            anomaly_data = []
            for idx in result['indices'][:20]:
                anomaly_data.append({
                    'Index': idx,
                    'Value': df[col].iloc[idx],
                    'Row Data': df.iloc[idx].to_dict()
                })
            st.dataframe(pd.DataFrame(anomaly_data), use_container_width=True)
        
        # Alert
        st.warning(f"""
        🚨 **Alert!** Found {result['count']} anomalies in {col}
        
        **Recommendation:** 
        - Review these values - they could indicate errors or valuable insights
        - Consider investigating the cause of these outliers
        - If these are errors, consider removing or correcting them
        """)
    else:
        st.success("✅ No anomalies detected! Your data looks clean.")

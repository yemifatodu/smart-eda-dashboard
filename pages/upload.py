import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time
from utils.data_processor import DataProcessor

def show():
    st.markdown('<h1 class="main-header">📤 Data Upload & Validation</h1>', unsafe_allow_html=True)
    
    # Create sample data if not exists
    create_sample_data()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Drop your CSV file here or click to browse",
            type=['csv', 'xlsx'],
            help="Upload CSV or Excel file with your data"
        )
        
        if uploaded_file is not None:
            # Process the file
            with st.spinner("Processing your data..."):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Store in session state
                    st.session_state.data = df
                    
                    # Process data
                    processor = DataProcessor()
                    processed = processor.process_data(df)
                    st.session_state.processed_data = processed
                    
                    st.success(f"✅ Successfully loaded {len(df):,} rows and {len(df.columns)} columns!")
                    
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
    
    with col2:
        # Sample data option
        st.markdown("### 📊 Sample Datasets")
        if st.button("📦 Load Superstore Dataset"):
            df = pd.read_csv('data/sample_superstore.csv')
            st.session_state.data = df
            processor = DataProcessor()
            processed = processor.process_data(df)
            st.session_state.processed_data = processed
            st.success("✅ Superstore dataset loaded!")
            st.rerun()
        
        if st.button("🌿 Load Iris Dataset"):
            from sklearn.datasets import load_iris
            iris = load_iris()
            df = pd.DataFrame(iris.data, columns=iris.feature_names)
            df['species'] = iris.target_names[iris.target]
            st.session_state.data = df
            processor = DataProcessor()
            processed = processor.process_data(df)
            st.session_state.processed_data = processed
            st.success("✅ Iris dataset loaded!")
            st.rerun()
    
    # Show data preview if loaded
    if st.session_state.data is not None:
        st.markdown("---")
        st.markdown("### 📋 Data Preview")  # <-- FIXED: changed markhead to markdown
        
        df = st.session_state.data
        processed = st.session_state.processed_data
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{df.shape[0]:,}")
        with col2:
            st.metric("Total Columns", df.shape[1])
        with col3:
            missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            st.metric("Missing Values", f"{missing_pct:.1f}%")
        with col4:
            quality_score = calculate_quality_score(df)
            st.session_state.data_quality_score = quality_score
            st.metric("Data Quality", f"{quality_score}%")
        
        # Data preview tabs
        tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "📈 Summary Stats", "ℹ️ Column Info"])
        
        with tab1:
            st.dataframe(df.head(100), use_container_width=True)
        
        with tab2:
            st.dataframe(processed['summary_stats'], use_container_width=True)
        
        with tab3:
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.dataframe(col_info, use_container_width=True)

def create_sample_data():
    """Create sample superstore data if it doesn't exist"""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    file_path = data_dir / 'sample_superstore.csv'
    if not file_path.exists():
        # Generate sample data
        np.random.seed(42)
        n = 1000
        
        categories = ['Furniture', 'Office Supplies', 'Technology']
        sub_categories = ['Chairs', 'Tables', 'Phones', 'Computers', 'Paper', 'Binders']
        regions = ['North', 'South', 'East', 'West']
        segments = ['Consumer', 'Corporate', 'Home Office']
        
        df = pd.DataFrame({
            'Order_ID': [f'ORD-{i:04d}' for i in range(n)],
            'Category': np.random.choice(categories, n),
            'Sub_Category': np.random.choice(sub_categories, n),
            'Region': np.random.choice(regions, n),
            'Segment': np.random.choice(segments, n),
            'Sales': np.random.uniform(10, 1000, n),
            'Quantity': np.random.randint(1, 10, n),
            'Discount': np.random.uniform(0, 0.5, n),
            'Profit': np.random.uniform(-100, 500, n),
            'Profit_Margin': np.random.uniform(0, 0.8, n),
            'Customer_Count': np.random.randint(1, 5, n)
        })
        
        df.to_csv(file_path, index=False)

def calculate_quality_score(df):
    """Calculate data quality score"""
    score = 100
    
    # Penalize for missing values
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    score -= missing_pct * 0.5
    
    # Penalize for duplicate rows
    duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
    score -= duplicate_pct * 0.3
    
    # Penalize for all-null columns
    null_columns = df.columns[df.isnull().all()].tolist()
    if null_columns:
        score -= len(null_columns) * 5
    
    return max(0, int(score))
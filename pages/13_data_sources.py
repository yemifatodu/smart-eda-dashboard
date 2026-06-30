import streamlit as st
import pandas as pd
import sqlite3
import requests
from pathlib import Path

def show():
    st.markdown('<h1 class="main-header">🔗 Multi-Data Sources</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Connect to Multiple Data Sources
    Import data from different sources and merge them together
    """)
    
    # Data source options
    source = st.selectbox(
        "Select Data Source",
        ["📁 Local File", "📊 SQL Database", "🌐 API/URL", "📈 Google Sheets"]
    )
    
    if source == "📁 Local File":
        show_local_file_upload()
    elif source == "📊 SQL Database":
        show_sql_connection()
    elif source == "🌐 API/URL":
        show_api_connection()
    elif source == "📈 Google Sheets":
        show_gsheet_connection()

def show_local_file_upload():
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=['csv', 'xlsx']
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded {len(df):,} rows from {uploaded_file.name}")
            
            if st.button("📥 Add to Analysis"):
                if 'multi_data' not in st.session_state:
                    st.session_state.multi_data = []
                st.session_state.multi_data.append(df)
                st.success("✅ Data added!")
        
        except Exception as e:
            st.error(f"Error loading file: {e}")

def show_sql_connection():
    st.info("Connect to SQL database")
    
    db_type = st.selectbox("Database Type", ["SQLite", "PostgreSQL", "MySQL"])
    
    if db_type == "SQLite":
        db_file = st.text_input("Database File Path", "data.db")
        table = st.text_input("Table Name", "sales_data")
        
        if st.button("🔌 Connect & Load"):
            try:
                conn = sqlite3.connect(db_file)
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 1000", conn)
                conn.close()
                
                st.success(f"✅ Loaded {len(df):,} rows from {table}")
                st.dataframe(df.head())
                
                if st.button("📥 Add to Analysis"):
                    if 'multi_data' not in st.session_state:
                        st.session_state.multi_data = []
                    st.session_state.multi_data.append(df)
                    st.success("✅ Data added!")
            
            except Exception as e:
                st.error(f"Error: {e}")

def show_api_connection():
    st.info("Load data from API")
    
    api_url = st.text_input("API URL", "https://api.example.com/data")
    headers = st.text_area("Headers (JSON)", '{"Authorization": "Bearer token"}')
    
    if st.button("🌐 Fetch Data"):
        try:
            import json
            headers_dict = json.loads(headers) if headers else {}
            response = requests.get(api_url, headers=headers_dict)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                st.success(f"✅ Loaded {len(df):,} rows from API")
                st.dataframe(df.head())
                
                if st.button("📥 Add to Analysis"):
                    if 'multi_data' not in st.session_state:
                        st.session_state.multi_data = []
                    st.session_state.multi_data.append(df)
                    st.success("✅ Data added!")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        
        except Exception as e:
            st.error(f"Error: {e}")

def show_gsheet_connection():
    st.info("Connect to Google Sheets (requires credentials)")
    st.warning("⚠️ Google Sheets integration requires additional setup")
    
    sheet_id = st.text_input("Google Sheet ID", "1ABC123...")
    sheet_name = st.text_input("Sheet Name", "Sheet1")
    
    if st.button("📊 Load Google Sheet"):
        st.info("Please set up Google Sheets API credentials")
        
    # Show existing multi-data
    if 'multi_data' in st.session_state and st.session_state.multi_data:
        st.markdown("---")
        st.subheader("📊 Data Sources Added")
        
        for idx, df in enumerate(st.session_state.multi_data):
            with st.expander(f"Dataset {idx+1} - {len(df):,} rows"):
                st.dataframe(df.head())
                if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.multi_data.pop(idx)
                    st.rerun()
        
        # Merge option
        if len(st.session_state.multi_data) > 1:
            if st.button("🔗 Merge All Data"):
                merged = pd.concat(st.session_state.multi_data, ignore_index=True)
                st.session_state.data = merged
                st.success(f"✅ Merged {len(merged):,} rows into main dataset!")
                st.rerun()

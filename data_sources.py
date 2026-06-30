import streamlit as st
import pandas as pd
import sqlite3
import requests
import re
import ipaddress
from urllib.parse import urlparse
from pathlib import Path

# Only allow alphanumeric + underscore table names (prevents SQL injection
# via string-built queries against user-supplied table names).
VALID_IDENTIFIER = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def show():
    st.markdown('<h1 class="main-header">🔗 Multi-Data Sources</h1>', unsafe_allow_html=True)

    st.markdown("""
    ### Connect to Multiple Data Sources
    Import data from different sources and merge them together
    """)

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
    MAX_SIZE_MB = 50
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel (max 50MB)",
        type=['csv', 'xlsx']
    )

    if uploaded_file:
        if uploaded_file.size > MAX_SIZE_MB * 1024 * 1024:
            st.error(f"❌ File too large. Max size is {MAX_SIZE_MB}MB.")
            return
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

        except Exception:
            st.error("Error loading file. Please check the format and try again.")


def show_sql_connection():
    st.info("Connect to SQL database")

    db_type = st.selectbox("Database Type", ["SQLite", "PostgreSQL", "MySQL"])

    if db_type == "SQLite":
        db_file = st.text_input("Database File Path", "data.db")
        table = st.text_input("Table Name", "sales_data")

        if st.button("🔌 Connect & Load"):
            # Validate the table name BEFORE it ever touches a query string.
            # This is the fix for the SQL injection in the original version,
            # which did f"SELECT * FROM {table} LIMIT 1000".
            if not VALID_IDENTIFIER.match(table):
                st.error("❌ Invalid table name. Use letters, numbers, and underscores only.")
                return
            try:
                conn = sqlite3.connect(db_file)
                # Table identifiers can't be parameterized with placeholders
                # in sqlite3, so we validate the identifier above instead.
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 1000", conn)
                conn.close()

                st.success(f"✅ Loaded {len(df):,} rows from {table}")
                st.dataframe(df.head())

                if st.button("📥 Add to Analysis"):
                    if 'multi_data' not in st.session_state:
                        st.session_state.multi_data = []
                    st.session_state.multi_data.append(df)
                    st.success("✅ Data added!")

            except Exception:
                st.error("Error connecting to database. Check the file path and table name.")
    else:
        st.info(f"{db_type} support requires connection credentials — coming soon.")


def _is_safe_url(url: str) -> bool:
    """Basic SSRF guard: only allow http(s), block requests aimed at
    localhost / private / link-local addresses so this can't be used to
    reach internal services if this app is ever self-hosted on a network."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname
        if not host:
            return False
        if host in ("localhost",):
            return False
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            pass  # host is a domain name, not an IP literal — allow it
        return True
    except Exception:
        return False


def show_api_connection():
    st.info("Load data from API")

    api_url = st.text_input("API URL", "https://api.example.com/data")
    headers = st.text_area("Headers (JSON)", '{"Authorization": "Bearer token"}')

    if st.button("🌐 Fetch Data"):
        if not _is_safe_url(api_url):
            st.error("❌ That URL isn't allowed (must be a public http/https address).")
            return
        try:
            import json
            headers_dict = json.loads(headers) if headers else {}
            response = requests.get(api_url, headers=headers_dict, timeout=10)

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
                st.error(f"Error {response.status_code} fetching data")

        except Exception:
            st.error("Error fetching from API. Check the URL and headers.")


def show_gsheet_connection():
    st.info("Connect to Google Sheets (requires credentials)")
    st.warning("⚠️ Google Sheets integration requires additional setup")

    sheet_id = st.text_input("Google Sheet ID", "1ABC123...")
    sheet_name = st.text_input("Sheet Name", "Sheet1")

    if st.button("📊 Load Google Sheet"):
        st.info("Please set up Google Sheets API credentials")

    if 'multi_data' in st.session_state and st.session_state.multi_data:
        st.markdown("---")
        st.subheader("📊 Data Sources Added")

        for idx, df in enumerate(st.session_state.multi_data):
            with st.expander(f"Dataset {idx+1} - {len(df):,} rows"):
                st.dataframe(df.head())
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.multi_data.pop(idx)
                    st.rerun()

        if len(st.session_state.multi_data) > 1:
            if st.button("🔗 Merge All Data"):
                merged = pd.concat(st.session_state.multi_data, ignore_index=True)
                st.session_state.data = merged
                st.success(f"✅ Merged {len(merged):,} rows into main dataset!")
                st.rerun()

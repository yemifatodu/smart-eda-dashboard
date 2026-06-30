import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def show():
    st.markdown('<h1 class="main-header">👥 Team Collaboration</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    st.markdown("### 👥 Team Features")
    st.caption("Share and collaborate on dashboards with your team")
    
    # Create team space
    if 'team_data' not in st.session_state:
        st.session_state.team_data = {
            'shared_dashboards': [],
            'comments': [],
            'members': []
        }
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Shared Dashboards", "💬 Comments", "👤 Team Members"])
    
    with tab1:
        show_shared_dashboards()
    
    with tab2:
        show_comments()
    
    with tab3:
        show_team_members()

def show_shared_dashboards():
    st.subheader("📊 Share Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        dashboard_name = st.text_input("Dashboard Name", "My Dashboard")
    
    with col2:
        share_type = st.selectbox("Share With", ["Team", "Public", "Private"])
    
    if st.button("📤 Share Dashboard", type="primary"):
        # Save current dashboard configuration
        dashboard = {
            'name': dashboard_name,
            'widgets': st.session_state.get('dashboard_widgets', []),
            'layout': st.session_state.get('dashboard_layout', {}),
            'shared_by': st.session_state.get('username', 'user'),
            'shared_at': datetime.now().isoformat(),
            'share_type': share_type,
            'views': 0
        }
        
        st.session_state.team_data['shared_dashboards'].append(dashboard)
        st.success(f"✅ Dashboard '{dashboard_name}' shared!")
        st.rerun()
    
    # Show shared dashboards
    st.markdown("---")
    st.subheader("📋 Shared Dashboards")
    
    if st.session_state.team_data['shared_dashboards']:
        for idx, dashboard in enumerate(st.session_state.team_data['shared_dashboards']):
            with st.expander(f"📊 {dashboard['name']} (Shared by: {dashboard['shared_by']})"):
                st.caption(f"Type: {dashboard['share_type']} | Views: {dashboard['views']}")
                st.caption(f"Shared: {dashboard['shared_at'][:16]}")
                
                if st.button("📂 Load Dashboard", key=f"load_{idx}"):
                    st.session_state.dashboard_widgets = dashboard['widgets']
                    st.session_state.dashboard_layout = dashboard['layout']
                    st.success("✅ Dashboard loaded!")
                    st.rerun()
                
                if st.button("❤️ Like", key=f"like_{idx}"):
                    st.success("👍 Liked!")
    else:
        st.info("No shared dashboards yet")

def show_comments():
    st.subheader("💬 Comments")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        comment = st.text_input("Add a comment")
    
    with col2:
        if st.button("💬 Post Comment"):
            if comment:
                st.session_state.team_data['comments'].append({
                    'user': st.session_state.get('username', 'user'),
                    'comment': comment,
                    'timestamp': datetime.now().isoformat()
                })
                st.success("✅ Comment posted!")
                st.rerun()
    
    # Show comments
    if st.session_state.team_data['comments']:
        for idx, comment in enumerate(st.session_state.team_data['comments']):
            st.info(f"**{comment['user']}** {comment['timestamp'][:16]}")
            st.write(comment['comment'])
            st.markdown("---")
    else:
        st.info("No comments yet")

def show_team_members():
    st.subheader("👤 Team Members")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_member = st.text_input("Add Team Member (email)")
    
    with col2:
        role = st.selectbox("Role", ["Admin", "Editor", "Viewer"])
    
    if st.button("➕ Add Member"):
        if new_member:
            st.session_state.team_data['members'].append({
                'email': new_member,
                'role': role,
                'joined': datetime.now().isoformat()
            })
            st.success(f"✅ Added {new_member}")
            st.rerun()
    
    # Show members
    if st.session_state.team_data['members']:
        members_df = pd.DataFrame(st.session_state.team_data['members'])
        st.dataframe(members_df, use_container_width=True)
    else:
        st.info("No team members yet")

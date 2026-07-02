import streamlit as st
import pandas as pd
from datetime import datetime
from utils.report_scheduler import ReportScheduler

def show():
    st.markdown('<h1 class="main-header">⏰ Auto-Report Scheduler</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    scheduler = ReportScheduler()
    
    st.subheader("📋 Create New Schedule")
    
    col1, col2 = st.columns(2)
    
    with col1:
        schedule_name = st.text_input("Schedule Name", "Weekly Sales Report")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
        email = st.text_input("Recipient Email", "your@email.com")
    
    with col2:
        report_title = st.text_input("Report Title", "Sales Performance Report")
        include_eda = st.checkbox("Include EDA Visualizations", True)
        include_models = st.checkbox("Include Model Results", st.session_state.model_results is not None)
    
    st.caption(f"📅 Next send: {get_next_send_preview(frequency)}")
    
    if st.button("📅 Create Schedule", type="primary"):
        report_config = {'title': report_title, 'include_eda': include_eda, 'include_models': include_models}
        schedule_id = scheduler.add_schedule(schedule_name, frequency, email, report_config)
        st.success(f"✅ Schedule created! ID: {schedule_id}")
        st.rerun()
    
    st.markdown("---")
    st.subheader("📋 Active Schedules")
    
    if scheduler.schedules:
        for sid, schedule in scheduler.schedules.items():
            with st.expander(f"📊 {schedule['name']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Frequency", schedule['frequency'])
                col2.metric("Recipient", schedule['email'])
                col3.metric("Created", schedule['created_at'][:10])
                if schedule.get('last_sent'):
                    st.caption(f"📨 Last sent: {schedule['last_sent'][:16]}")
                if schedule.get('next_send'):
                    st.caption(f"⏰ Next send: {schedule['next_send'][:16]}")
                if st.button(f"🗑️ Delete", key=f"del_{sid}"):
                    scheduler.delete_schedule(sid)
                    st.rerun()
    else:
        st.info("No active schedules. Create one above!")

def get_next_send_preview(frequency):
    from datetime import datetime, timedelta
    now = datetime.now()
    if frequency == 'daily':
        next_send = now + timedelta(days=1)
    elif frequency == 'weekly':
        next_send = now + timedelta(days=7)
    elif frequency == 'monthly':
        next_send = now + timedelta(days=30)
    else:
        next_send = now + timedelta(days=1)
    return next_send.strftime('%Y-%m-%d %H:%M')

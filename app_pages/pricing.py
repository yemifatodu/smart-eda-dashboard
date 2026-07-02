import streamlit as st
from utils.usage_tracker import UsageTracker

def show():
    st.markdown('<h1 class="main-header">💎 Upgrade to Pro</h1>', unsafe_allow_html=True)
    
    tracker = UsageTracker()
    user_id = st.session_state.get('username', 'default')
    
    # Check if pro
    is_pro = tracker.get_user_usage(user_id).get('is_pro', False)
    
    if is_pro:
        st.success("✅ You're a Pro member!")
        return
    
    # Show trial status
    remaining = tracker.get_remaining_analyses(user_id)
    st.info(f"🎯 Free Trial: {remaining} analyses remaining")
    
    st.markdown("---")
    
    # FREEMIUM MODEL
    st.markdown("### 🚀 Freemium Plans")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Free
        **/month**
        
        ✅ 5 analyses/month
        ✅ Sample data only
        ✅ Basic EDA
        ✅ Basic charts
        ❌ No PDF reports
        ❌ No scheduling
        
        **Best for**: Testing
        """)
        if st.button("🚀 Continue Free", key="free", use_container_width=True):
            st.info("You're already on the Free plan!")
    
    with col2:
        st.markdown("""
        ### 💎 Pro Monthly
        **/month**
        
        ✅ Unlimited analyses
        ✅ Custom data upload
        ✅ All 15+ features
        ✅ PDF reports
        ✅ Auto-scheduling
        ✅ AI insights
        ✅ Priority support
        
        **Best for**: Small businesses
        """)
        if st.button("📅 Subscribe Monthly", key="pro_monthly", use_container_width=True):
            st.session_state.selected_plan = "Pro Monthly (/mo)"
            st.rerun()
    
    with col3:
        st.markdown("""
        ### 🏆 Pro Annual
        **/year**
        **(/month)**
        
        ✅ All Pro features
        ✅ Save /year
        ✅ 2 months free
        ✅ Best value
        
        **Best for**: Regular users
        """)
        if st.button("📅 Subscribe Annual", key="pro_annual", use_container_width=True):
            st.session_state.selected_plan = "Pro Annual (/yr)"
            st.rerun()
    
    # TEAM AND ENTERPRISE
    st.markdown("---")
    st.markdown("### 👥 Team & Enterprise Plans")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Team Plan
        **/month**
        
        ✅ 5 users included
        ✅ Team collaboration
        ✅ Shared dashboards
        ✅ Admin dashboard
        ✅ Priority support
        ✅ All Pro features
        
        **Best for**: Teams
        """)
        if st.button("👥 Start Team Plan", key="team", use_container_width=True):
            st.info("📧 Contact us for team setup: team@yourapp.com")
    
    with col2:
        st.markdown("""
        ### Enterprise Plan
        **/month**
        
        ✅ Unlimited users
        ✅ API access
        ✅ White-label branding
        ✅ SLA guarantee
        ✅ Dedicated support
        ✅ Custom features
        
        **Best for**: Large orgs
        """)
        if st.button("🏢 Contact Enterprise", key="enterprise", use_container_width=True):
            st.info("📧 Contact us: enterprise@yourapp.com")
    
    # ONE-TIME PURCHASE
    st.markdown("---")
    st.markdown("### 💰 One-Time Purchase (Lifetime)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Basic License
        ** once**
        
        ✅ All features
        ✅ 1 user license
        ✅ Lifetime updates
        ✅ Email support
        
        **Best for**: Individuals
        """)
        if st.button("💳 Buy Basic", key="basic_license", use_container_width=True):
            st.session_state.selected_plan = "Basic License ()"
            st.rerun()
    
    with col2:
        st.markdown("""
        ### Pro License
        ** once**
        
        ✅ All features
        ✅ 3 user licenses
        ✅ Lifetime updates
        ✅ Priority support
        
        **Best for**: Small teams
        """)
        if st.button("💳 Buy Pro License", key="pro_license", use_container_width=True):
            st.session_state.selected_plan = "Pro License ()"
            st.rerun()
    
    with col3:
        st.markdown("""
        ### Enterprise License
        ** once**
        
        ✅ All features
        ✅ Unlimited users
        ✅ Custom branding
        ✅ Dedicated support
        ✅ Lifetime updates
        
        **Best for**: Large orgs
        """)
        if st.button("💳 Buy Enterprise", key="enterprise_license", use_container_width=True):
            st.session_state.selected_plan = "Enterprise License ()"
            st.rerun()
    
    # Payment processing
    if 'selected_plan' in st.session_state:
        st.markdown("---")
        with st.expander("💳 Complete Purchase", expanded=True):
            st.write(f"Selected: **{st.session_state.selected_plan}**")
            
            with st.form("payment_form"):
                st.text_input("Card Number", placeholder="4242 4242 4242 4242")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Expiry Date", placeholder="MM/YY")
                with col2:
                    st.text_input("CVC", placeholder="123")
                
                if st.form_submit_button("💳 Pay Now", type="primary"):
                    # Simulate payment
                    import time
                    with st.spinner("Processing payment..."):
                        time.sleep(2)
                    
                    # Upgrade user
                    tracker.upgrade_to_pro(user_id)
                    st.success(f"🎉 Success! You're now on {st.session_state.selected_plan}!")
                    st.session_state.selected_plan = None
                    st.rerun()

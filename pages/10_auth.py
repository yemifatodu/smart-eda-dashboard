import streamlit as st
import hashlib
import json
from pathlib import Path

class AuthManager:
    def __init__(self):
        self.users_file = Path('data/users.json')
        self.users_file.parent.mkdir(exist_ok=True)
        self.load_users()
    
    def load_users(self):
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Create default admin user
            self.users = {
                'admin': {
                    'password': self.hash_password('admin123'),
                    'name': 'Administrator',
                    'role': 'admin',
                    'created_at': pd.Timestamp.now().isoformat()
                }
            }
            self.save_users()
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        if username in self.users:
            return self.users[username]['password'] == self.hash_password(password)
        return False
    
    def add_user(self, username, password, name=''):
        if username not in self.users:
            self.users[username] = {
                'password': self.hash_password(password),
                'name': name or username,
                'role': 'user',
                'created_at': pd.Timestamp.now().isoformat()
            }
            self.save_users()
            return True
        return False
    
    def change_password(self, username, new_password):
        if username in self.users:
            self.users[username]['password'] = self.hash_password(new_password)
            self.save_users()
            return True
        return False

def show():
    st.markdown('<h1 class="main-header">🔐 User Authentication</h1>', unsafe_allow_html=True)
    
    # Initialize auth manager
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    auth = st.session_state.auth_manager
    
    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    if not st.session_state.logged_in:
        show_login(auth)
    else:
        show_dashboard(auth)

def show_login(auth):
    st.markdown("### 🔑 Login")
    st.caption("Default: username='admin', password='admin123'")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("🔐 Login", type="primary"):
                if auth.verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        
        if st.button("📝 Create New User"):
            st.session_state.show_signup = True
        
        if st.session_state.get('show_signup', False):
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                new_name = st.text_input("Display Name")
                
                if st.form_submit_button("📝 Create Account"):
                    if auth.add_user(new_username, new_password, new_name):
                        st.success("✅ Account created! Please login.")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error("❌ Username already exists")

def show_dashboard(auth):
    username = st.session_state.username
    user_info = auth.users.get(username, {})
    
    st.success(f"✅ Logged in as: **{user_info.get('name', username)}**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Your Dashboard")
        
        # Show user stats
        st.metric("User", username)
        st.metric("Role", user_info.get('role', 'user'))
        st.caption(f"Member since: {user_info.get('created_at', 'Unknown')[:10]}")
    
    with col2:
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        if st.button("🔑 Change Password"):
            st.session_state.show_change_password = True
    
    # Change password
    if st.session_state.get('show_change_password', False):
        with st.form("change_password_form"):
            current = st.text_input("Current Password", type="password")
            new = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔑 Update Password"):
                if auth.verify_user(username, current):
                    if new == confirm:
                        if auth.change_password(username, new):
                            st.success("✅ Password updated successfully!")
                            st.session_state.show_change_password = False
                            st.rerun()
                    else:
                        st.error("❌ Passwords do not match")
                else:
                    st.error("❌ Current password is incorrect")
    
    # User management (admin only)
    if user_info.get('role') == 'admin':
        st.markdown("---")
        st.markdown("### 👥 User Management")
        
        users_df = pd.DataFrame([
            {
                'Username': u,
                'Name': info.get('name', ''),
                'Role': info.get('role', 'user'),
                'Created': info.get('created_at', '')[:10]
            }
            for u, info in auth.users.items()
        ])
        st.dataframe(users_df, use_container_width=True)
        
        # Admin: Create new user
        with st.expander("➕ Create New User (Admin)"):
            col1, col2 = st.columns(2)
            with col1:
                new_user = st.text_input("New Username")
            with col2:
                new_pass = st.text_input("New Password", type="password")
            
            if st.button("Create User"):
                if auth.add_user(new_user, new_pass, new_user):
                    st.success(f"✅ User '{new_user}' created!")
                    st.rerun()
                else:
                    st.error("❌ User already exists")
    
    # Quick access to app features
    st.markdown("---")
    st.markdown("### 🚀 Quick Access")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Upload Data", use_container_width=True):
            st.session_state.current_page = "📤 Upload"
            st.rerun()
    with col2:
        if st.button("💬 Ask AI", use_container_width=True):
            st.session_state.current_page = "💬 Ask AI"
            st.rerun()
    with col3:
        if st.button("📊 EDA", use_container_width=True):
            st.session_state.current_page = "📊 EDA"
            st.rerun()

import streamlit as st
import pandas as pd
import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

# How many PBKDF2 rounds to use when hashing passwords.
PBKDF2_ITERATIONS = 200_000


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
            # Create a default admin user with a RANDOM password that is
            # only ever shown once, in the server logs, on first run.
            # Never hardcode or display default credentials in the UI.
            admin_password = os.environ.get('ADMIN_BOOTSTRAP_PASSWORD') or secrets.token_urlsafe(12)
            salt = secrets.token_hex(16)
            self.users = {
                'admin': {
                    'salt': salt,
                    'password': self.hash_password(admin_password, salt),
                    'name': 'Administrator',
                    'role': 'admin',
                    'created_at': pd.Timestamp.now().isoformat()
                }
            }
            self.save_users()
            print("=" * 60)
            print("FIRST RUN: created admin account.")
            print(f"  username: admin")
            print(f"  password: {admin_password}")
            print("Change this password immediately after logging in.")
            print("=" * 60)

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
        # Best-effort lock down file permissions (no-op on Windows)
        try:
            os.chmod(self.users_file, 0o600)
        except OSError:
            pass

    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), PBKDF2_ITERATIONS
        ).hex()

    def verify_user(self, username, password):
        user = self.users.get(username)
        if not user:
            return False
        # Support legacy unsalted records gracefully (forces a rehash on next change)
        salt = user.get('salt')
        if not salt:
            return False
        expected = self.hash_password(password, salt)
        # Constant-time comparison to avoid timing attacks
        return hmac.compare_digest(expected, user['password'])

    def add_user(self, username, password, name=''):
        if username in self.users:
            return False
        salt = secrets.token_hex(16)
        self.users[username] = {
            'salt': salt,
            'password': self.hash_password(password, salt),
            'name': name or username,
            'role': 'user',
            'created_at': pd.Timestamp.now().isoformat()
        }
        self.save_users()
        return True

    def change_password(self, username, new_password):
        if username not in self.users:
            return False
        salt = secrets.token_hex(16)
        self.users[username]['salt'] = salt
        self.users[username]['password'] = self.hash_password(new_password, salt)
        self.save_users()
        return True


def show():
    st.markdown('<h1 class="main-header">🔐 User Authentication</h1>', unsafe_allow_html=True)

    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()

    auth = st.session_state.auth_manager

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        show_login(auth)
    else:
        show_dashboard(auth)


def show_login(auth):
    st.markdown("### 🔑 Login")

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
                    if len(new_password) < 8:
                        st.error("❌ Password must be at least 8 characters")
                    elif auth.add_user(new_username, new_password, new_name):
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

    if st.session_state.get('show_change_password', False):
        with st.form("change_password_form"):
            current = st.text_input("Current Password", type="password")
            new = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("🔑 Update Password"):
                if not auth.verify_user(username, current):
                    st.error("❌ Current password is incorrect")
                elif new != confirm:
                    st.error("❌ Passwords do not match")
                elif len(new) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    auth.change_password(username, new)
                    st.success("✅ Password updated successfully!")
                    st.session_state.show_change_password = False
                    st.rerun()

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

        with st.expander("➕ Create New User (Admin)"):
            col1, col2 = st.columns(2)
            with col1:
                new_user = st.text_input("New Username", key="admin_new_user")
            with col2:
                new_pass = st.text_input("New Password", type="password", key="admin_new_pass")

            if st.button("Create User"):
                if len(new_pass) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif auth.add_user(new_user, new_pass, new_user):
                    st.success(f"✅ User '{new_user}' created!")
                    st.rerun()
                else:
                    st.error("❌ User already exists")

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

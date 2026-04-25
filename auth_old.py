import json
import bcrypt
import streamlit as st
from pathlib import Path

class AuthManager:
    """Secure authentication manager with bcrypt password hashing"""
    
    def __init__(self, users_file='users.json'):
        self.users_file = Path(users_file)
        self.users = self._load_users()
        
    def _load_users(self):
        """Load users from JSON file"""
        if not self.users_file.exists():
            # Create default admin user
            default_users = {
                "admin": {
                    "name": "Administrator",
                    "password": self._hash_password("admin123"),
                    "team": "ALL",
                    "role": "admin"
                }
            }
            self._save_users(default_users)
            return default_users
        
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=4)
    
    def _hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate(self, username, password):
        """Authenticate user and return user info"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if self._verify_password(password, user['password']):
            return {
                'username': username,
                'name': user['name'],
                'team': user['team'],
                'role': user['role']
            }
        return None
    
    def add_user(self, username, name, password, team, role):
        """Add new user (admin only)"""
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'name': name,
            'password': self._hash_password(password),
            'team': team,
            'role': role
        }
        self._save_users(self.users)
        return True, "User added successfully"
    
    def delete_user(self, username):
        """Delete user (admin only)"""
        if username == 'admin':
            return False, "Cannot delete admin user"
        
        if username not in self.users:
            return False, "User not found"
        
        del self.users[username]
        self._save_users(self.users)
        return True, "User deleted successfully"
    
    def change_password(self, username, new_password):
        """Change user password"""
        if username not in self.users:
            return False, "User not found"
        
        self.users[username]['password'] = self._hash_password(new_password)
        self._save_users(self.users)
        return True, "Password changed successfully"
    
    def update_user_team(self, username, new_team):
        """Update user's assigned team"""
        if username not in self.users:
            return False, "User not found"
        
        self.users[username]['team'] = new_team
        self._save_users(self.users)
        return True, "Team updated successfully"
    
    def get_all_users(self):
        """Get all users (admin only)"""
        return self.users
    
    def list_users_for_display(self):
        """Get users without sensitive data"""
        return {
            username: {
                'name': user['name'],
                'team': user['team'],
                'role': user['role']
            }
            for username, user in self.users.items()
        }


def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None


def login_page(auth_manager):
    """Render login page with improved UI"""
    
    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 5rem auto;
            padding: 3rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-title {
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .login-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .stTextInput > div > div > input {
            background-color: rgba(255,255,255,0.9);
            border-radius: 10px;
            border: none;
            padding: 12px;
            font-size: 1rem;
        }
        .stButton > button {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: 1.1rem;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🏏 APL Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Andhra Premier League 2025</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Secure Login")
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="visible")
            password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="visible")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    user_info = auth_manager.authenticate(username, password)
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.success(f"✅ Welcome, {user_info['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
        
        # Help section (collapsible)
        with st.expander("ℹ️ Need Help?"):
            st.info("""
            **Forgot your credentials?**
            
            Please contact your system administrator for:
            - Password reset
            - Username recovery
            - Access issues
            
            **First time user?**
            
            Your administrator will provide you with:
            - Your unique username
            - Temporary password (change after first login)
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>
            <p>🔒 Secure Authentication System</p>
            <p style='font-size: 0.8rem; margin-top: 0.5rem;'>Powered by ZenmindsCricketData</p>
        </div>
        """, unsafe_allow_html=True)


def logout():
    """Handle logout"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()


def render_user_management(auth_manager):
    """Render user management interface (admin only)"""
    st.markdown("## 👥 User Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Add User", "View Users", "Delete User", "Change Password"])
    
    with tab1:
        st.markdown("### ➕ Add New User")
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_team = st.selectbox("Assign Team", [
                "Amaravati Royals",
                "Bheemavaram Bulls", 
                "Kakinada Kings",
                "Royals of Rayalaseema",
                "Tungabhadra Warriors",
                "Simhari Vizaz Lions",
                "Vijayawada Sunshiners"
            ])
            new_role = st.selectbox("Role", ["team_user", "admin"])
            
            submit = st.form_submit_button("Add User")
            
            if submit:
                if new_username and new_name and new_password:
                    success, message = auth_manager.add_user(
                        new_username, new_name, new_password, new_team, new_role
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.markdown("### 📋 All Users")
        users = auth_manager.list_users_for_display()
        if users:
            import pandas as pd
            df = pd.DataFrame.from_dict(users, orient='index')
            df.index.name = 'Username'
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")
    
    with tab3:
        st.markdown("### 🗑️ Delete User")
        users = list(auth_manager.get_all_users().keys())
        users = [u for u in users if u != 'admin']
        
        if users:
            with st.form("delete_user_form"):
                delete_username = st.selectbox("Select User to Delete", users)
                confirm = st.checkbox("I confirm deletion")
                submit = st.form_submit_button("Delete User")
                
                if submit:
                    if confirm:
                        success, message = auth_manager.delete_user(delete_username)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Please confirm deletion")
        else:
            st.info("No users available to delete")
    
    with tab4:
        st.markdown("### 🔑 Change Password")
        users = list(auth_manager.get_all_users().keys())
        
        with st.form("change_password_form"):
            change_username = st.selectbox("Select User", users)
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Change Password")
            
            if submit:
                if new_password and new_password == confirm_password:
                    success, message = auth_manager.change_password(change_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    st.error("Please enter a password")
import streamlit as st
from config_leagues import get_league_config, validate_league_password

def show_league_auth():
    """Display league password authentication page"""
    
    # Get selected league
    if 'selected_league' not in st.session_state:
        st.session_state.page = 'league_selector'
        st.rerun()
    
    league_code = st.session_state.selected_league
    league_config = get_league_config(league_code)
    
    if not league_config:
        st.error("Invalid league selected")
        return
    
    # Custom CSS
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 5rem auto;
            padding: 3rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .league-badge {
            background: linear-gradient(135deg, """ + league_config['color_primary'] + """ 0%, """ + league_config['color_secondary'] + """ 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            display: inline-block;
            font-weight: 600;
            margin-bottom: 2rem;
        }
        
        .auth-title {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .auth-subtitle {
            color: #666;
            margin-bottom: 2rem;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, """ + league_config['color_primary'] + """ 0%, """ + league_config['color_secondary'] + """ 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # League badge
        st.markdown(f'<div style="text-align: center;"><span class="league-badge">🏏 {league_config["name"]}</span></div>', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'<h2 class="auth-title" style="text-align: center;">League Access</h2>', unsafe_allow_html=True)
        st.markdown(f'<p class="auth-subtitle" style="text-align: center;">Enter league password to continue</p>', unsafe_allow_html=True)
        
        # Password input
        password = st.text_input(
            "League Password",
            type="password",
            key="league_password_input",
            placeholder="Enter password"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔓 Access Dashboard", key="access_btn", use_container_width=True):
                if validate_league_password(league_code, password):
                    st.session_state.league_authenticated = True
                    st.session_state.page = 'team_login'
                    st.success(f"✅ Access granted to {league_config['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password. Please try again.")
        
        with col_btn2:
            if st.button("← Back", key="back_btn", use_container_width=True):
                st.session_state.page = 'league_selector'
                st.rerun()
        
        # Info
        st.markdown("---")
        st.info(f"""
        **📋 League Information:**
        - **Teams:** {len(league_config['teams'])} teams
        - **Season:** {', '.join(league_config['years'])}
        - **Status:** Active
        
        🔒 Contact your league administrator for access credentials.
        """)
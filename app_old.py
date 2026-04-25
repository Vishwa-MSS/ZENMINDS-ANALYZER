import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add modules to path
sys.path.append(str(Path(__file__).parent))

# Import authentication and filtering modules
from auth import AuthManager, init_session_state, login_page, logout, render_user_management
from data_filter import DataFilter, render_global_filters, apply_global_filters

# Import dashboard modules
from modules import batting_module, bowling_module, partnerships_module, extras_module, wides_module

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="APL 2025 Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.4rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 600;
    }
    
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px 28px;
        font-weight: 600;
        color: #495057;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        border-color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
        padding: 1rem 1.5rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        font-weight: 600;
        color: #495057;
    }
    
    /* Logo container */
    .logo-container {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* User info card */
    .user-info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Security badge */
    .security-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(17, 153, 142, 0.3);
    }
    
    .security-badge-admin {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Filter section */
    .filter-section {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# DATA LOADING
# =========================
@st.cache_data
def load_cricket_data():
    """Load the APL 2025 dataset"""
    try:
        df = pd.read_csv("APL_2025_LeagueData.csv")
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()
        # Clean team names
        if 'team1_battingfirst' in df.columns:
            df['team1_battingfirst'] = df['team1_battingfirst'].str.strip()
        if 'team2_battingsecond' in df.columns:
            df['team2_battingsecond'] = df['team2_battingsecond'].str.strip()
        return df
    except FileNotFoundError:
        st.error("❌ Dataset not found! Please ensure 'APL_2025_LeagueData.csv' is in the same directory.")
        st.stop()

# =========================
# MAIN APPLICATION
# =========================
def main():
    # Initialize session state
    init_session_state()
    
    # Initialize authentication manager
    auth_manager = AuthManager('users.json')
    
    # =========================
    # AUTHENTICATION CHECK
    # =========================
    if not st.session_state.authenticated:
        login_page(auth_manager)
        return
    
    # =========================
    # AUTHENTICATED USER UI
    # =========================
    user_info = st.session_state.user_info
    
    # =========================
    # SIDEBAR - USER INFO & LOGOUT
    # =========================
    with st.sidebar:
        # Logo section
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            from PIL import Image
            logo = Image.open("logo.png")
            st.image(logo, use_container_width=True)
        except:
            st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h2 style='color: white; margin: 0;'>🏏 Zenminds</h2>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 0.5rem;'>Cricket Data</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info card
        st.markdown('<div class="user-info-card">', unsafe_allow_html=True)
        st.markdown(f"### 👤 {user_info['name']}")
        
        if user_info['role'] == 'admin':
            st.markdown('<span class="security-badge security-badge-admin">🔓 ADMIN</span>', unsafe_allow_html=True)
            st.caption("Full system access")
        else:
            st.markdown(f"**Team:** {user_info['team']}")
            st.markdown('<span class="security-badge">🔒 TEAM USER</span>', unsafe_allow_html=True)
            st.caption("Team-restricted access")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
    
    # =========================
    # LOAD DATA
    # =========================
    df = load_cricket_data()
    
    # =========================
    # DATA FILTERING (SECURITY LAYER)
    # =========================
    data_filter = DataFilter(df, user_info)
    filtered_data = data_filter.get_filtered_data()
    
    # Display access message
    st.sidebar.info(data_filter.get_display_message())
    
    # =========================
    # GLOBAL FILTERS
    # =========================
    selected_teams, selected_matches = render_global_filters(data_filter, key_prefix="main")
    
    # Apply global filters
    final_data = apply_global_filters(filtered_data, selected_teams, selected_matches)
    
    # =========================
    # MAIN HEADER
    # =========================
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="header-title">🏏 Andhra Premier League 2025</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Professional Cricket Analytics Platform</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================
    # ADMIN USER MANAGEMENT
    # =========================
    if user_info['role'] == 'admin':
        with st.expander("👥 User Management (Admin Only)", expanded=False):
            render_user_management(auth_manager)
        st.markdown("---")
    
    # =========================
    # MAIN DASHBOARD TABS
    # =========================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏏 Batting Analysis", 
        "🎯 Bowling Analysis", 
        "🤝 Batting Partnerships", 
        "➕ Extras Analysis",
        "🎾 Wides Analysis"
    ])
    
    with tab1:
        st.markdown("## 🏏 Batting Analysis")
        st.markdown("---")
        batting_module.render_batting_dashboard(final_data, selected_teams, selected_matches)
    
    with tab2:
        st.markdown("## 🎯 Bowling Analysis")
        st.markdown("---")
        bowling_module.render_bowling_dashboard(final_data, selected_teams, selected_matches)
    
    with tab3:
        st.markdown("## 🤝 Batting Partnerships")
        st.markdown("---")
        partnerships_module.render_partnerships_dashboard(final_data, selected_teams, selected_matches)
    
    with tab4:
        st.markdown("## ➕ Extras Analysis")
        st.markdown("---")
        extras_module.render_extras_dashboard(final_data, selected_teams, selected_matches)
    
    with tab5:
        st.markdown("## 🎾 Wides Analysis")
        st.markdown("---")
        wides_module.render_wides_dashboard(final_data, selected_teams, selected_matches)
    
    # =========================
    # FOOTER
    # =========================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p><strong>Andhra Premier League 2025 - Comprehensive Analytics Platform</strong></p>
        <p>Powered by <strong>ZenmindsCricketData</strong> | Data · Video · Intelligence</p>
        <p style='font-size: 0.9rem; margin-top: 10px;'>
            🔒 Secure Multi-User Platform | Role-Based Access Control | Real-time Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
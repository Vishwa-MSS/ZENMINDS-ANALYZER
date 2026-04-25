import streamlit as st
from config_leagues import get_all_leagues

def show_league_selector():
    """Display league selection page"""
    
    # Custom CSS for league cards
    st.markdown("""
        <style>
        .league-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin: 1rem 0;
        }
        
        .league-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .league-card h2 {
            color: white;
            font-size: 2rem;
            margin: 0;
            font-weight: 700;
        }
        
        .league-card p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            margin-top: 0.5rem;
        }
        
        .mpl-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .main-title {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.3rem;
            margin-bottom: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-title">🏏 Cricket Analytics Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Professional Multi-League Cricket Analytics Platform</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get all leagues
    leagues = get_all_leagues()
    
    # Create two columns for league cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="league-card">
                <h2>🏏 Andhra Premier League</h2>
                <p>Complete analytics for APL 2025</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">
                    📊 7 Teams | 📈 Full Season Stats | 🎯 Advanced Analytics
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter APL Dashboard", key="apl_button", use_container_width=True):
            st.session_state.selected_league = 'APL'
            st.session_state.page = 'league_auth'
            st.rerun()
    
    with col2:
        st.markdown("""
            <div class="league-card mpl-card">
                <h2>👑 Maharaja Premier League</h2>
                <p>Complete analytics for MPL 2025</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">
                    📊 6 Teams | 📈 Full Season Stats | 🎯 Advanced Analytics
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter MPL Dashboard", key="mpl_button", use_container_width=True):
            st.session_state.selected_league = 'MPL'
            st.session_state.page = 'league_auth'
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem 0;'>
            <p style='font-size: 0.9rem;'>
                🔒 Secure Access | 📊 Real-time Analytics | 🎯 Team Insights
            </p>
            <p style='font-size: 0.8rem; margin-top: 1rem;'>
                Powered by ZenMinds Analytics © 2025
            </p>
        </div>
    """, unsafe_allow_html=True)
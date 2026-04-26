import pandas as pd
import streamlit as st

class DataFilter:
    """Secure data filtering based on user role and team assignment"""
    
    def __init__(self, df, user_info):
        self.df = df
        self.user_info = user_info
        self.role = user_info['role']
        self.assigned_team = user_info['team']
    
    def get_filtered_data(self):
        """
        Get data filtered based on user's role and team assignment.
        CRITICAL: This is the main security boundary - all data access must go through this.
        """
        if self.role == 'admin':
            # Admin sees all data
            return self.df
        else:
            # Team users only see their team's data
            return self._filter_by_team(self.assigned_team)
    
    def _filter_by_team(self, team_name):
        """Filter dataset to only include matches where the specified team played"""
        df_copy = self.df.copy()
        
        # Clean team names
        df_copy['team1_battingfirst'] = df_copy['team1_battingfirst'].str.strip()
        df_copy['team2_battingsecond'] = df_copy['team2_battingsecond'].str.strip()
        
        # Filter: team is either batting first OR batting second
        filtered_df = df_copy[
            (df_copy['team1_battingfirst'] == team_name) | 
            (df_copy['team2_battingsecond'] == team_name)
        ]
        
        return filtered_df
    
    def get_available_teams(self):
        """
        Get list of teams available to the user.
        Admin: all teams
        Team user: only their assigned team
        """
        if self.role == 'admin':
            teams = list(set(
                list(self.df['team1_battingfirst'].dropna().unique()) +
                list(self.df['team2_battingsecond'].dropna().unique())
            ))
            return sorted([t.strip() for t in teams if t])
        else:
            # Team users see only their team
            return [self.assigned_team]
    
    def get_available_matches(self, selected_teams=None):
        """
        Get list of available match numbers based on user role and selected teams.
        """
        filtered_data = self.get_filtered_data()
        
        if selected_teams and len(selected_teams) > 0:
            # Further filter by selected teams
            filtered_data = filtered_data[
                (filtered_data['team1_battingfirst'].isin(selected_teams)) |
                (filtered_data['team2_battingsecond'].isin(selected_teams))
            ]
        
        matches = sorted(filtered_data['match_no'].unique())
        return matches
    
    def apply_match_filter(self, df, selected_matches):
        """Apply match number filter to dataframe"""
        if selected_matches and len(selected_matches) > 0:
            return df[df['match_no'].isin(selected_matches)]
        return df
    
    def apply_team_filter(self, df, selected_teams):
        """Apply additional team filter to already filtered dataframe"""
        if selected_teams and len(selected_teams) > 0:
            return df[
                (df['team1_battingfirst'].isin(selected_teams)) |
                (df['team2_battingsecond'].isin(selected_teams))
            ]
        return df
    
    def get_display_message(self):
        """Get display message for current user's data access"""
        if self.role == 'admin':
            return "🔓 Admin Access: Viewing all teams"
        else:
            return f"🔒 Team Access: {self.assigned_team}"


def render_global_filters(data_filter, key_prefix=""):
    """
    Render global filters (Teams and Matches) that work across all tabs.
    These filters respect user role and team assignment.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🎯 Global Filters")
    
    # Team Filter
    available_teams = data_filter.get_available_teams()
    
    if data_filter.role == 'admin':
        st.sidebar.markdown("### 🏏 Select Teams")
        selected_teams = st.sidebar.multiselect(
            "Choose teams to analyze",
            options=available_teams,
            default=[],
            key=f"{key_prefix}_team_filter"
        )
        
        if not selected_teams:
            selected_teams = available_teams  # If none selected, show all
    else:
        # Team users don't get to choose - automatically set to their team
        selected_teams = [data_filter.assigned_team]
        st.sidebar.markdown("### 🏏 Your Team")
        st.sidebar.info(f"**{data_filter.assigned_team}**")
    
    # Match Filter
    available_matches = data_filter.get_available_matches(selected_teams)
    
    st.sidebar.markdown("### 🎮 Select Matches")
    selected_matches = st.sidebar.multiselect(
        "Choose matches (leave empty for all)",
        options=available_matches,
        default=[],
        key=f"{key_prefix}_match_filter"
    )
    
    if not selected_matches:
        selected_matches = available_matches  # If none selected, show all
    
    # Display filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Active Filters")
    st.sidebar.info(f"""
    **Teams:** {len(selected_teams)}  
    **Matches:** {len(selected_matches)}
    """)
    
    return selected_teams, selected_matches


def apply_global_filters(df, selected_teams, selected_matches):
    """
    Apply the global team and match filters to a dataframe.
    This should be used by all dashboard modules.
    """
    filtered_df = df.copy()
    
    # Apply team filter
    if selected_teams:
        filtered_df = filtered_df[
            (filtered_df['team1_battingfirst'].isin(selected_teams)) |
            (filtered_df['team2_battingsecond'].isin(selected_teams))
        ]
    
    # Apply match filter
    if selected_matches:
        filtered_df = filtered_df[filtered_df['match_no'].isin(selected_matches)]
    
    return filtered_df


def filter_dashboard(df, league_config, available_years=None):
    """
    Main dashboard rendering function with league-specific branding
    """
    import streamlit as st
    from modules import batting_module, bowling_module, partnerships_module, extras_module, wides_module, report_module
    
    # Get league branding
    league_name = league_config['name']
    league_short = league_config['short_name']
    color_primary = league_config['color_primary']
    color_secondary = league_config['color_secondary']
    
    # Custom CSS for league branding
    st.markdown(f"""
        <style>
        .main-header {{
            background: linear-gradient(135deg, {color_primary} 0%, {color_secondary} 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .main-title {{
            color: white;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .main-subtitle {{
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">🏏 {league_name} Analytics</h1>
            <p class="main-subtitle">Season 2025 • Powered by ZenMinds Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get user info
    if 'user_info' not in st.session_state:
        user_info = {
            'name': st.session_state.get('username', 'User'),
            'team': st.session_state.get('assigned_team', 'ALL'),
            'role': st.session_state.get('role', 'team_user')
        }
    else:
        user_info = st.session_state.user_info
    
    # Initialize data filter
    data_filter = DataFilter(df, user_info)
    
    # Sidebar - User info
    st.sidebar.markdown(f"""
        <div style='background: linear-gradient(135deg, {color_primary} 0%, {color_secondary} 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem;'>👤 {user_info['name']}</h2>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                {'🔓 Admin Access' if user_info['role'] == 'admin' else f"🏏 {user_info['team']}"}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Year Filter (NEW)
    if available_years and len(available_years) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📅 Season Filter")
        
        # Multi-select for years
        selected_years = st.sidebar.multiselect(
            "Select Season(s):",
            options=available_years,
            default=st.session_state.get('selected_years', [available_years[0]]),
            key="year_filter",
            help="Select one or multiple seasons to analyze"
        )
        
        # Update session state and reload data if years changed
        if selected_years != st.session_state.get('selected_years', []):
            st.session_state.selected_years = selected_years
            st.rerun()
        
        # Display selected years info
        if len(selected_years) > 1:
            st.sidebar.info(f"📊 Comparing {len(selected_years)} seasons: {', '.join(map(str, selected_years))}")
        elif len(selected_years) == 1:
            st.sidebar.success(f"📊 Viewing season: {selected_years[0]}")
        else:
            st.sidebar.warning("⚠️ Please select at least one season")
            return
    
    # Global filters
    selected_teams, selected_matches = render_global_filters(data_filter, key_prefix="main")
    
    # Apply filters
    final_data = apply_global_filters(df, selected_teams, selected_matches)
    
    # Display message
    if len(final_data) == 0:
        st.warning("⚠️ No data available for selected filters")
        return
    
    # Add User Management button for admins
    if user_info['role'] == 'admin':
        st.sidebar.markdown("---")
        if st.sidebar.button("👥 Manage Users", use_container_width=True, key="user_mgmt_btn"):
            st.session_state.show_user_management = not st.session_state.get('show_user_management', False)
            st.rerun()
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.league_authenticated = False
        st.session_state.page = 'league_selector'
        st.rerun()
    
    # Show User Management if enabled
    if st.session_state.get('show_user_management', False) and user_info['role'] == 'admin':
        from auth_multi import AuthManager, render_user_management
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, {0} 0%, {1} 100%); 
                        padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
                <h1 style='color: white; margin: 0;'>👥 User Management</h1>
                <p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem;'>
                    Manage team users for {2}
                </p>
            </div>
        """.format(color_primary, color_secondary, league_name), unsafe_allow_html=True)
        
        # Get league-specific user file
        league_short = league_config['short_name'].lower()
        users_file = f'users_{league_short}.json'
        auth_manager = AuthManager(users_file=users_file)
        
        # Get teams list
        teams_list = league_config['teams']
        
        # Render user management
        render_user_management(auth_manager, teams_list)
        
        if st.button("← Back to Dashboard", key="back_to_dash"):
            st.session_state.show_user_management = False
            st.rerun()
        
        return  # Don't show dashboard tabs when in user management
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏏 Batting",
        "🎯 Bowling", 
        "🤝 Partnerships",
        "➕ Extras",
        "📊 Wides",
        "📋 Report"
    ])
    
    with tab1:
        batting_module.render_batting_dashboard(final_data, selected_teams, selected_matches)
    
    with tab2:
        bowling_module.render_bowling_dashboard(final_data, selected_teams, selected_matches)
    
    with tab3:
        partnerships_module.render_partnerships_dashboard(final_data, selected_teams, selected_matches)
    
    with tab4:
        extras_module.render_extras_dashboard(final_data, selected_teams, selected_matches)
    
    with tab5:
        wides_module.render_wides_dashboard(final_data, selected_teams, selected_matches)
    
    with tab6:
        report_module.render_report_dashboard(final_data, selected_teams, selected_matches)
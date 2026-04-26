import streamlit as st
import pandas as pd
from config_leagues import get_league_config
from league_selector import show_league_selector
from league_auth import show_league_auth
from auth_multi import login_page
from data_filter import filter_dashboard
import os

# Page configuration
st.set_page_config(
    page_title="Cricket Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'league_selector'

if 'selected_league' not in st.session_state:
    st.session_state.selected_league = None

if 'league_authenticated' not in st.session_state:
    st.session_state.league_authenticated = False

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'role' not in st.session_state:
    st.session_state.role = None

if 'assigned_team' not in st.session_state:
    st.session_state.assigned_team = None

def load_league_data(league_code, selected_years=None):
    """Load data for selected league and years"""
    from config_leagues import get_league_config, get_available_years
    
    league_config = get_league_config(league_code)
    if not league_config:
        st.error(f"League configuration not found for: {league_code}")
        return None
    
    data_folder = league_config['data_folder']
    
    if not os.path.exists(data_folder):
        st.error(f"Data folder not found: {data_folder}")
        return None
    
    # If no years selected, return empty dataframe structure
    if not selected_years or len(selected_years) == 0:
        st.warning("Please select at least one year to view data")
        return None
    
    try:
        all_dataframes = []
        
        # Load data for each selected year
        for year in selected_years:
            file_path = os.path.join(data_folder, f"{league_config['short_name']}_{year}.csv")
            
            if not os.path.exists(file_path):
                st.warning(f"Data file not found for year {year}: {file_path}")
                continue
            
            df = pd.read_csv(file_path)
            
            # Add year column
            df['season_year'] = year
            
            all_dataframes.append(df)
        
        if len(all_dataframes) == 0:
            st.error("No data files found for selected years")
            return None
        
        # Combine all years
        df = pd.concat(all_dataframes, ignore_index=True)
        
        # Standardize column names - strip whitespace
        df.columns = df.columns.str.strip()
        
        # Rename columns to match expected format
        column_mapping = {
            'runs_off_bat': 'runs_offbat',
            'team1_batting_first': 'team1_battingfirst',
            'team2_batting_second': 'team2_battingsecond'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Standardize pace_or_spin values to lowercase
        if 'pace_or_spin' in df.columns:
            df['pace_or_spin'] = df['pace_or_spin'].str.lower()
        
        # Standardize bowling_hand and batting_hand to title case
        if 'bowling_hand' in df.columns:
            df['bowling_hand'] = df['bowling_hand'].str.title()
        if 'batting_hand' in df.columns:
            df['batting_hand'] = df['batting_hand'].str.title()
        
        # Convert boolean columns
        bool_columns = ['is_wicket', 'is_boundary']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].map({
                    'TRUE': True, 'True': True, True: True,
                    'FALSE': False, 'False': False, False: False
                }).fillna(False)
        
        # Fill NaN in categorical columns
        categorical_cols = ['Wicket_type', 'extra_type']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # Convert numeric columns
        numeric_cols = ['runs_offbat', 'extras', 'match_no', 'innings', 'over', 'ball']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def main():
    """Main application routing"""
    
    # Route to appropriate page
    if st.session_state.page == 'league_selector':
        show_league_selector()
    
    elif st.session_state.page == 'league_auth':
        show_league_auth()
    
    elif st.session_state.page == 'team_login':
        if not st.session_state.league_authenticated:
            st.session_state.page = 'league_auth'
            st.rerun()
        
        # Get league config
        league_config = get_league_config(st.session_state.selected_league)
        
        # Show team login page
        login_page(league_config)
    
    elif st.session_state.page == 'dashboard':
        if not st.session_state.authenticated:
            st.session_state.page = 'team_login'
            st.rerun()
        
        # Load league data
        league_code = st.session_state.selected_league
        league_config = get_league_config(league_code)
        
        # Get available years and update config
        from config_leagues import update_available_years
        update_available_years()
        
        available_years = league_config.get('available_years', [])
        
        if not available_years:
            st.error(f"No data files found in {league_config['data_folder']}")
            st.info(f"Please ensure CSV files are named as: {league_config['short_name']}_YYYY.csv")
            if st.button("← Back to League Selection"):
                st.session_state.page = 'league_selector'
                st.session_state.authenticated = False
                st.session_state.league_authenticated = False
                st.rerun()
            return
        
        # Initialize selected years in session state
        if 'selected_years' not in st.session_state:
            st.session_state.selected_years = [available_years[0]] if available_years else []
        
        # Load data for selected years
        df = load_league_data(league_code, st.session_state.selected_years)
        
        if df is not None:
            # Show dashboard with league-specific branding
            filter_dashboard(df, league_config, available_years)
        else:
            if st.button("← Back to League Selection"):
                st.session_state.page = 'league_selector'
                st.session_state.authenticated = False
                st.session_state.league_authenticated = False
                st.rerun()

if __name__ == "__main__":
    main()
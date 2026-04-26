# League Configurations for Multi-League Analyzer

LEAGUES = {
    'APL': {
        'name': 'Andhra Premier League',
        'short_name': 'APL',
        'password': 'APL@#zenminds',
        'logo': 'apl_logo.png',
        'data_folder': 'data/APL',  # Folder containing year-wise CSV files
        'color_primary': '#667eea',
        'color_secondary': '#764ba2',
        'teams': [
            'Amaravati Royals',
            'Bhimavaram Bulls',
            'Kakinada Kings',
            'Royals of Rayalaseema',
            'Simhadri Vizag Lions',
            'Tungabhadra Warriors',
            'Vijayawada Sun Shiners'
        ],
        'available_years': []  # Will be auto-detected from folder
    },
    'MPL': {
        'name': 'Maharaja Premier League',
        'short_name': 'MPL',
        'password': 'MPL@#zenminds',
        'logo': 'mpl_logo.png',
        'data_folder': 'data/MPL',  # Folder containing year-wise CSV files
        'color_primary': '#f093fb',
        'color_secondary': '#f5576c',
        'teams': [
            'Bengaluru Blasters',
            'Gulbarga Mystics',
            'Hubli Tigers',
            'Mangaluru Dragons',
            'Mysore Warriors',
            'Shivamogga Lions'
        ],
        'available_years': []  # Will be auto-detected from folder
    }
}

# Default users for each league (same structure for both)
DEFAULT_USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'team': 'All Teams'
    }
}

def get_league_config(league_code):
    """Get configuration for a specific league"""
    return LEAGUES.get(league_code, None)

def get_all_leagues():
    """Get list of all available leagues"""
    return LEAGUES

def validate_league_password(league_code, password):
    """Validate password for a league"""
    league = LEAGUES.get(league_code)
    if league:
        return league['password'] == password
    return False

def get_available_years(league_code):
    """Auto-detect available years from data folder"""
    import os
    import re
    
    league = LEAGUES.get(league_code)
    if not league:
        return []
    
    data_folder = league['data_folder']
    if not os.path.exists(data_folder):
        return []
    
    years = []
    # Look for files like APL_2024.csv, APL_2025.csv, MPL_2024.csv, etc.
    pattern = re.compile(rf"{league['short_name']}_(\d{{4}})\.csv", re.IGNORECASE)
    
    for filename in os.listdir(data_folder):
        match = pattern.match(filename)
        if match:
            year = int(match.group(1))
            years.append(year)
    
    return sorted(years, reverse=True)  # Most recent first

def update_available_years():
    """Update available years for all leagues"""
    for league_code in LEAGUES.keys():
        LEAGUES[league_code]['available_years'] = get_available_years(league_code)
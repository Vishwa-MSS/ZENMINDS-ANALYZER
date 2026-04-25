# League Configurations for Multi-League Analyzer

LEAGUES = {
    'APL': {
        'name': 'Andhra Premier League',
        'short_name': 'APL',
        'password': 'APL@#zenminds',
        'logo': 'apl_logo.png',
        'data_file': 'APL_2025_LeagueData.csv',
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
        'years': ['2025']  # Will expand in future
    },
    'MPL': {
        'name': 'Maharaja Premier League',
        'short_name': 'MPL',
        'password': 'MPL@#zenminds',
        'logo': 'mpl_logo.png',
        'data_file': 'maharaja_bbb_final.csv',
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
        'years': ['2025']  # Will expand in future
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
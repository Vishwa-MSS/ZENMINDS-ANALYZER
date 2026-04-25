# APL 2025 Dashboard Configuration
# Edit this file to customize your dashboard settings

# =========================
# TEAM CONFIGURATION
# =========================
# List all teams in your league (one per line)
TEAMS = [
    "Amaravati Royals",
    "Guntur Gladiators",
    "Kakinada Kings",
    "Rayalaseema Royals",
    "Tirupati Tigers",
    "Visakhapatnam Warriors",
    "Vijayawada Commanders"
]

# =========================
# DASHBOARD SETTINGS
# =========================
# Dashboard title
DASHBOARD_TITLE = "Andhra Premier League 2025"

# Dashboard subtitle
DASHBOARD_SUBTITLE = "Advanced Cricket Analytics Dashboard"

# Company/Organization name
ORGANIZATION_NAME = "ZenmindsCricketData"

# Tagline
TAGLINE = "Data · Video · Intelligence"

# =========================
# DATA SETTINGS
# =========================
# Dataset filename
DATASET_FILE = "APL_2025_LeagueData.csv"

# Minimum balls for player statistics
MIN_BALLS_FOR_PLAYER_STATS = 10

# Minimum overs for bowler statistics
MIN_OVERS_FOR_BOWLER_STATS = 2

# =========================
# SECURITY SETTINGS
# =========================
# Default admin username (cannot be changed after first run)
DEFAULT_ADMIN_USERNAME = "admin"

# Default admin password (CHANGE THIS IMMEDIATELY AFTER FIRST LOGIN!)
DEFAULT_ADMIN_PASSWORD = "admin123"

# Session timeout (in minutes) - Not yet implemented
SESSION_TIMEOUT_MINUTES = 60

# =========================
# UI CUSTOMIZATION
# =========================
# Primary color (hex code)
PRIMARY_COLOR = "#1e3c72"

# Secondary color (hex code)
SECONDARY_COLOR = "#2a5298"

# Accent color (hex code)
ACCENT_COLOR = "#3498DB"

# Success color (hex code)
SUCCESS_COLOR = "#27ae60"

# Warning color (hex code)
WARNING_COLOR = "#f39c12"

# Error color (hex code)
ERROR_COLOR = "#e74c3c"

# =========================
# CHART SETTINGS
# =========================
# Default chart height
DEFAULT_CHART_HEIGHT = 400

# Color palette for team charts
TEAM_COLORS = [
    '#3498DB',  # Blue
    '#E74C3C',  # Red
    '#2ECC71',  # Green
    '#F39C12',  # Orange
    '#9B59B6',  # Purple
    '#1ABC9C',  # Turquoise
    '#E67E22',  # Carrot
]

# =========================
# PHASE DEFINITIONS
# =========================
# Cricket match phases
PHASES = {
    "Powerplay": (0, 5),
    "Middle Overs 1": (6, 9),
    "Middle Overs 2": (10, 14),
    "Death Overs": (15, 19),
}

# =========================
# FEATURE FLAGS
# =========================
# Enable/disable features
ENABLE_USER_MANAGEMENT = True
ENABLE_DATA_EXPORT = False  # Disable for security
ENABLE_RAW_DATA_VIEW = False  # Disable for security
ENABLE_LOGO = True

# =========================
# ADVANCED SETTINGS
# =========================
# Cache timeout (in seconds)
CACHE_TTL_SECONDS = 3600

# Maximum file upload size (in MB)
MAX_UPLOAD_SIZE_MB = 200

# Enable debug mode (shows detailed errors)
DEBUG_MODE = False

# =========================
# CONTACT INFORMATION
# =========================
SUPPORT_EMAIL = "support@zenmindscricketdata.com"
WEBSITE = "www.zenmindscricketdata.com"

# =========================
# NOTES
# =========================
# - Edit values above to customize your dashboard
# - Restart the app after making changes
# - Keep this file secure (contains default credentials)
# - For advanced customization, edit the Python source files directly
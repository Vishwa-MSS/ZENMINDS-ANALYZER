"""
Data Cleaning Utility for APL 2025 Dataset
Run this script to clean and validate your cricket dataset before using it in the dashboard
"""

import pandas as pd
import sys

def clean_dataset(input_file='APL_2025_LeagueData.csv', output_file='APL_2025_LeagueData_cleaned.csv'):
    """
    Clean and validate the APL cricket dataset
    """
    
    print("🔍 Loading dataset...")
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} rows")
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found!")
        sys.exit(1)
    
    print("\n🧹 Cleaning data...")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower()
    print("✅ Standardized column names")
    
    # Clean team names
    if 'team1_battingfirst' in df.columns:
        df['team1_battingfirst'] = df['team1_battingfirst'].str.strip()
    
    if 'team2_battingsecond' in df.columns:
        df['team2_battingsecond'] = df['team2_battingsecond'].str.strip()
    
    print("✅ Cleaned team names")
    
    # Clean player names
    for col in ['batsman', 'non_striker', 'bowler']:
        if col in df.columns:
            df[col] = df[col].str.strip()
    
    print("✅ Cleaned player names")
    
    # Validate required columns
    required_columns = [
        'match_no', 'innings', 'over', 'ball',
        'batsman', 'non_striker', 'bowler',
        'runs_offbat', 'extras', 'is_wicket',
        'team1_battingfirst', 'team2_battingsecond'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"\n⚠️  Warning: Missing columns: {missing_columns}")
    else:
        print("✅ All required columns present")
    
    # Data quality checks
    print("\n📊 Data Quality Report:")
    print(f"Total matches: {df['match_no'].nunique()}")
    print(f"Total teams: {len(set(df['team1_battingfirst'].unique()) | set(df['team2_battingsecond'].unique()))}")
    print(f"Total players: {df['batsman'].nunique()}")
    print(f"Total bowlers: {df['bowler'].nunique()}")
    print(f"Date range: {df.shape[0]} balls")
    
    # Check for nulls in critical columns
    print("\n🔍 Null Values Check:")
    null_counts = df[required_columns].isnull().sum()
    if null_counts.sum() > 0:
        print("⚠️  Found null values:")
        print(null_counts[null_counts > 0])
    else:
        print("✅ No null values in critical columns")
    
    # List all teams
    all_teams = sorted(set(df['team1_battingfirst'].unique()) | set(df['team2_battingsecond'].unique()))
    print("\n🏏 Teams in dataset:")
    for i, team in enumerate(all_teams, 1):
        print(f"  {i}. {team}")
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    print(f"\n💾 Cleaned dataset saved to: {output_file}")
    print("✅ Data cleaning complete!")
    
    return df


def validate_for_dashboard(df):
    """
    Additional validation specific to dashboard requirements
    """
    
    print("\n🎯 Dashboard Compatibility Check:")
    
    checks_passed = 0
    total_checks = 6
    
    # Check 1: Match numbers are numeric
    if pd.api.types.is_numeric_dtype(df['match_no']):
        print("✅ Match numbers are numeric")
        checks_passed += 1
    else:
        print("❌ Match numbers should be numeric")
    
    # Check 2: Innings are 1 or 2
    if df['innings'].isin([1, 2]).all():
        print("✅ Innings values are valid (1 or 2)")
        checks_passed += 1
    else:
        print("❌ Innings should only contain 1 or 2")
    
    # Check 3: Runs are numeric
    if pd.api.types.is_numeric_dtype(df['runs_offbat']):
        print("✅ Runs are numeric")
        checks_passed += 1
    else:
        print("❌ Runs should be numeric")
    
    # Check 4: Over numbers are valid
    if df['over'].between(0, 20).all():
        print("✅ Over numbers are valid (0-20)")
        checks_passed += 1
    else:
        print("⚠️  Some over numbers are outside 0-20 range")
    
    # Check 5: Teams are consistent
    team1_count = df['team1_battingfirst'].nunique()
    team2_count = df['team2_battingsecond'].nunique()
    if team1_count == team2_count:
        print(f"✅ Team names are consistent ({team1_count} teams)")
        checks_passed += 1
    else:
        print(f"⚠️  Team name inconsistency: team1={team1_count}, team2={team2_count}")
    
    # Check 6: Pace/spin is populated
    if 'pace_or_spin' in df.columns:
        null_pct = (df['pace_or_spin'].isnull().sum() / len(df)) * 100
        if null_pct < 5:
            print(f"✅ Pace/Spin data is {100-null_pct:.1f}% complete")
            checks_passed += 1
        else:
            print(f"⚠️  Pace/Spin data is {null_pct:.1f}% missing")
    
    print(f"\n📊 Dashboard Compatibility: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Dataset is fully compatible with the dashboard!")
    elif checks_passed >= total_checks - 1:
        print("✅ Dataset is mostly compatible with minor issues")
    else:
        print("⚠️  Dataset may have compatibility issues")
    
    return checks_passed == total_checks


if __name__ == "__main__":
    print("="*60)
    print("APL 2025 Dataset Cleaning Utility")
    print("ZenmindsCricketData")
    print("="*60)
    
    # Clean the dataset
    df_cleaned = clean_dataset()
    
    # Validate for dashboard
    validate_for_dashboard(df_cleaned)
    
    print("\n" + "="*60)
    print("You can now use the cleaned dataset with the dashboard!")
    print("="*60)
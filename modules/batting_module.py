import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_batting_dashboard(df, selected_teams, selected_matches):
    """
    Render the batting analysis dashboard
    This is adapted from the original batting.py to work within the main app
    """
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_teams:
        filtered_df = filtered_df[
            (filtered_df['team1_battingfirst'].isin(selected_teams)) |
            (filtered_df['team2_battingsecond'].isin(selected_teams))
        ]
    
    if selected_matches:
        filtered_df = filtered_df[filtered_df['match_no'].isin(selected_matches)]
    
    # Create total runs
    filtered_df['total_runs'] = filtered_df['runs_offbat'] + filtered_df['extras']
    
    # Phase creation
    def get_phase(over):
        if 1 <= over <= 6:
            return "Powerplay"
        elif 7 <= over <= 15:
            return "Middle Overs (7-15)"
        elif 7 <= over <= 10:
            return "Middle Overs 1"
        elif 11 <= over <= 15:
            return "Middle Overs 2"
        elif 16 <= over <= 20:
            return "Death Overs"
        else:
            return "Other"

    filtered_df['phase'] = filtered_df['over'].apply(get_phase)
    
    # Batting team
    filtered_df['batting_team'] = filtered_df['team1_battingfirst'].fillna(filtered_df['team2_battingsecond'])
    
    # =========================
    # SIDEBAR FILTERS (TAB-SPECIFIC)
    # =========================
    st.sidebar.markdown("### 🎯 Batting Filters")
    
    phase = st.sidebar.selectbox(
        "Select Phase",
        ["Powerplay", "Middle Overs (7-15)", "Middle Overs 1", "Middle Overs 2", "Death Overs", "Entire Innings"],
        key="batting_phase"
    )
    
    innings = st.sidebar.selectbox(
        "Select Innings",
        ["1st Innings", "2nd Innings", "Both Innings"],
        key="batting_innings"
    )
    
    # =========================
    # APPLY TAB FILTERS
    # =========================
    tab_filtered_df = filtered_df.copy()
    
    if phase != "Entire Innings":
        tab_filtered_df = tab_filtered_df[tab_filtered_df['phase'] == phase]
    
    if innings == "1st Innings":
        tab_filtered_df = tab_filtered_df[tab_filtered_df['innings'] == 1]
    elif innings == "2nd Innings":
        tab_filtered_df = tab_filtered_df[tab_filtered_df['innings'] == 2]
    
    # =========================
    # TEAM CHART
    # =========================
    st.subheader("📊 Batting Breakdown")
    
    grp = tab_filtered_df.groupby('batting_team').agg(
        innings=('match_no', 'nunique'),
        runs=('total_runs', 'sum'),
        balls=('ball', 'count'),
        wickets=('is_wicket', 'sum')
    ).reset_index()
    
    if not grp.empty:
        grp['run_rate'] = grp['runs'] / (grp['balls'] / 6)
        grp['avg_wkts'] = grp['wickets'] / grp['innings']
        
        dot_balls = tab_filtered_df[tab_filtered_df['runs_offbat'] == 0].groupby('batting_team')['ball'].count()
        grp['avg_dot_balls'] = grp['batting_team'].map(dot_balls).fillna(0) / grp['innings']
        
        grp = grp.sort_values(by='run_rate', ascending=False)
        
        fig = go.Figure()
        
        fig.add_bar(
            x=grp['batting_team'], 
            y=grp['innings'], 
            name="Innings",
            text=grp['innings'].round(0).astype(int),
            textposition='outside',
            textfont=dict(size=11)
        )
        fig.add_bar(
            x=grp['batting_team'], 
            y=grp['avg_wkts'], 
            name="Avg Wkts",
            text=grp['avg_wkts'].round(1),
            textposition='outside',
            textfont=dict(size=11)
        )
        fig.add_bar(
            x=grp['batting_team'], 
            y=grp['run_rate'], 
            name="Run Rate",
            text=grp['run_rate'].round(1),
            textposition='outside',
            textfont=dict(size=11)
        )
        fig.add_bar(
            x=grp['batting_team'], 
            y=grp['avg_dot_balls'], 
            name="Avg Dot Balls",
            text=grp['avg_dot_balls'].round(1),
            textposition='outside',
            textfont=dict(size=11)
        )
        
        fig.update_layout(
            barmode='group',
            template="plotly_white",
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        st.plotly_chart(fig, use_container_width=True, key="batting_breakdown_chart")
    else:
        st.warning("No data available for selected filters")
    
    # =========================
    # PLAYER TABLE
    # =========================
    if selected_teams and len(selected_teams) == 1:
        st.subheader(f"📋 Player Stats - {selected_teams[0]}")
        
        player_stats = tab_filtered_df.groupby('batsman').agg(
            runs=('runs_offbat', 'sum'),
            balls=('ball', 'count'),
            dismissals=('is_wicket', 'sum')
        ).reset_index()
        
        player_stats = player_stats[player_stats['balls'] >= 10]
        
        if not player_stats.empty:
            player_stats['strike_rate'] = (player_stats['runs'] / player_stats['balls']) * 100
            player_stats = player_stats.sort_values(by='strike_rate', ascending=False)
            
            st.dataframe(player_stats, use_container_width=True)
        else:
            st.warning("No players with minimum 10 balls")
    
    # =========================
    # PACE & SPIN ANALYSIS
    # =========================
    def pace_spin_analysis(data, title):
        grp = data.groupby('batting_team').agg(
            runs=('total_runs', 'sum'),
            balls=('ball', 'count'),
            wickets=('is_wicket', 'sum')
        ).reset_index()
        
        grp = grp[grp['balls'] > 0]
        
        # FIXED: Calculate Strike Rate (runs per 100 balls), not economy rate
        grp['strike_rate'] = (grp['runs'] / grp['balls']) * 100
        grp['balls_per_wicket'] = grp['balls'] / grp['wickets'].replace(0, 1)
        
        # Averages (for quadrant lines)
        avg_sr = grp['strike_rate'].mean()
        avg_bpw = grp['balls_per_wicket'].mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=grp['balls_per_wicket'],
            y=grp['strike_rate'],
            mode='markers+text',
            text=grp['batting_team'],
            textposition="top center",
            marker=dict(size=12, color='#667eea')
        ))
        
        # Average lines
        fig.add_vline(x=avg_bpw, line_dash="dash", line_color="red", annotation_text=f"Avg: {avg_bpw:.1f}")
        fig.add_hline(y=avg_sr, line_dash="dash", line_color="red", annotation_text=f"Avg: {avg_sr:.1f}")
        
        fig.update_layout(
            title=title,
            xaxis_title="Balls per Wicket",
            yaxis_title="Strike Rate (runs per 100 balls)",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    st.subheader("⚡ Batting vs Pace & Spin Analysis")
    
    col1, col2 = st.columns(2)
    
    # Pace
    pace_df = tab_filtered_df[tab_filtered_df['pace_or_spin'] == "pace"]
    
    with col1:
        st.plotly_chart(
            pace_spin_analysis(pace_df, "Batting vs Pace"),
            use_container_width=True,
            key="batting_vs_pace_chart"
        )
    
    # Spin
    spin_df = tab_filtered_df[tab_filtered_df['pace_or_spin'] == "spin"]
    
    with col2:
        st.plotly_chart(
            pace_spin_analysis(spin_df, "Batting vs Spin"),
            use_container_width=True,
            key="batting_vs_spin_chart"
        )
    
    # =========================
    # AVERAGE 1ST INNINGS SCORES
    # =========================
    st.subheader("📊 Average 1st Innings Scores")
    
    first_innings_df = filtered_df[filtered_df['innings'] == 1]
    
    # Match-level aggregation
    match_scores = first_innings_df.groupby(['match_no', 'batting_team'])['total_runs'].sum().reset_index()
    
    team_avg = match_scores.groupby('batting_team')['total_runs'].mean().reset_index()
    team_avg = team_avg.sort_values('total_runs', ascending=False)
    
    # League average
    league_avg = team_avg['total_runs'].mean()
    
    # Plot
    fig_avg = go.Figure()
    
    fig_avg.add_bar(
        x=team_avg['batting_team'],
        y=team_avg['total_runs'],
        text=team_avg['total_runs'].round(0),
        textposition='outside',
        marker=dict(color='#5B9BD5')
    )
    
    # Average line
    fig_avg.add_hline(
        y=league_avg,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average = {round(league_avg, 1)}",
        annotation_position="right"
    )
    
    fig_avg.update_layout(
        title="Average 1st Innings Scores",
        xaxis_title="",
        yaxis_title="Average Score",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_avg, use_container_width=True, key="batting_avg_runs_comparison")
    
    # =========================
    # TEAMS SCORING ABOVE LEAGUE AVERAGE
    # =========================
    st.subheader("📈 Teams Scoring Above League Average")
    
    # Count matches where score > league avg
    above_avg = match_scores.copy()
    above_avg['above_avg'] = above_avg['total_runs'] > league_avg
    
    count_df = above_avg.groupby('batting_team')['above_avg'].sum().reset_index()
    count_df.columns = ['batting_team', 'matches_above_avg']
    count_df = count_df.sort_values('matches_above_avg', ascending=False)
    
    # Plot
    fig_count = go.Figure()
    
    fig_count.add_bar(
        x=count_df['batting_team'],
        y=count_df['matches_above_avg'],
        text=count_df['matches_above_avg'],
        textposition='outside',
        marker=dict(color='#5B9BD5')
    )
    
    fig_count.update_layout(
        title=f"Teams Scoring More Than League Average of {round(league_avg, 1)} in 1st Innings",
        xaxis_title="",
        yaxis_title="No. of Matches",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_count, use_container_width=True, key="batting_above_avg_count")
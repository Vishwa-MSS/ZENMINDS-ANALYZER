import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_player_stats_dashboard(df, selected_teams, selected_matches):
    """
    Render comprehensive player statistics dashboard
    Shows batting and bowling stats with team, innings, and phase filters
    """
    
    # Apply global filters
    filtered_df = df.copy()
    
    if selected_teams:
        filtered_df = filtered_df[
            (filtered_df['team1_battingfirst'].isin(selected_teams)) |
            (filtered_df['team2_battingsecond'].isin(selected_teams))
        ]
    
    if selected_matches:
        filtered_df = filtered_df[filtered_df['match_no'].isin(selected_matches)]
    
    # Create phase column
    def get_phase(over):
        if 1 <= over <= 6:
            return "Powerplay (1-6)"
        elif 7 <= over <= 15:
            return "Middle Overs (7-15)"
        elif 16 <= over <= 20:
            return "Death Overs (16-20)"
        else:
            return "Other"
    
    filtered_df['phase'] = filtered_df['over'].apply(get_phase)
    filtered_df['total_runs'] = filtered_df['runs_offbat'] + filtered_df['extras']
    
    # Create two main sections
    st.markdown("## 👥 PLAYER STATISTICS")
    st.markdown("*Complete season statistics for individual players*")
    
    tabs = st.tabs(["🏏 Batting Stats", "🎯 Bowling Stats"])
    
    # ==========================================
    # TAB 1: BATTING STATISTICS
    # ==========================================
    with tabs[0]:
        render_batting_stats(filtered_df)
    
    # ==========================================
    # TAB 2: BOWLING STATISTICS
    # ==========================================
    with tabs[1]:
        render_bowling_stats(filtered_df)


def render_batting_stats(filtered_df):
    """Render detailed batting statistics"""
    
    st.markdown("### 🏏 Batting Statistics")
    
    # Sidebar filters for batting
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏏 Batting Stats Filters")
    
    # Get batting teams
    filtered_df['batting_team'] = filtered_df.apply(
        lambda row: row['team1_battingfirst'] if row['innings'] == 1 else row['team2_battingsecond'],
        axis=1
    )
    
    all_teams = sorted(filtered_df['batting_team'].unique())
    
    # Team filter
    selected_team_batting = st.sidebar.selectbox(
        "Select Team",
        options=all_teams,
        key="batting_stats_team"
    )
    
    # Innings filter
    innings_option = st.sidebar.selectbox(
        "Select Innings",
        options=["Both Innings", "1st Innings", "2nd Innings"],
        key="batting_stats_innings"
    )
    
    # Phase filter
    phase_option = st.sidebar.selectbox(
        "Select Phase",
        options=["Entire Innings", "Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"],
        key="batting_stats_phase"
    )
    
    # Apply filters
    batting_df = filtered_df[filtered_df['batting_team'] == selected_team_batting].copy()
    
    if innings_option == "1st Innings":
        batting_df = batting_df[batting_df['innings'] == 1]
    elif innings_option == "2nd Innings":
        batting_df = batting_df[batting_df['innings'] == 2]
    
    if phase_option != "Entire Innings":
        batting_df = batting_df[batting_df['phase'] == phase_option]
    
    # Calculate batting statistics
    if len(batting_df) > 0:
        batting_stats = batting_df.groupby('batsman').agg(
            runs=('runs_offbat', 'sum'),
            balls=('ball', 'count'),
            dismissals=('is_wicket', 'sum'),
            fours=('runs_offbat', lambda x: (x == 4).sum()),
            sixes=('runs_offbat', lambda x: (x == 6).sum()),
            dots=('runs_offbat', lambda x: (x == 0).sum())
        ).reset_index()
        
        # Calculate additional metrics
        batting_stats['strike_rate'] = (batting_stats['runs'] / batting_stats['balls'] * 100).round(2)
        batting_stats['average'] = (batting_stats['runs'] / batting_stats['dismissals'].replace(0, 1)).round(2)
        batting_stats['boundaries'] = batting_stats['fours'] + batting_stats['sixes']
        batting_stats['dot_percentage'] = (batting_stats['dots'] / batting_stats['balls'] * 100).round(1)
        
        # Filter players with minimum 10 balls
        batting_stats = batting_stats[batting_stats['balls'] >= 10]
        
        if not batting_stats.empty:
            # Sort by runs
            batting_stats = batting_stats.sort_values('runs', ascending=False).reset_index(drop=True)
            
            # Display title with filters
            st.markdown(f"#### 📊 {selected_team_batting} - Batting Statistics")
            st.markdown(f"*Filters: {innings_option} | {phase_option}*")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Runs", f"{batting_stats['runs'].sum():,}")
            with col2:
                st.metric("Total Balls", f"{batting_stats['balls'].sum():,}")
            with col3:
                st.metric("Boundaries", f"{batting_stats['boundaries'].sum():,}")
            with col4:
                st.metric("Team Strike Rate", f"{(batting_stats['runs'].sum() / batting_stats['balls'].sum() * 100):.2f}")
            
            st.markdown("---")
            
            # Display table
            display_stats = batting_stats[[
                'batsman', 'runs', 'balls', 'fours', 'sixes', 'boundaries',
                'dismissals', 'strike_rate', 'average', 'dot_percentage'
            ]].copy()
            
            # Rename columns for display
            display_stats.columns = [
                'Batsman', 'Runs', 'Balls', '4s', '6s', 'Boundaries',
                'Dismissals', 'Strike Rate', 'Average', 'Dot %'
            ]
            
            # Style the dataframe
            st.dataframe(
                display_stats,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Visualization - Top 10 Run Scorers
            st.markdown("---")
            st.markdown("#### 📈 Top 10 Run Scorers")
            
            top_10 = batting_stats.head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_10['batsman'],
                y=top_10['runs'],
                text=top_10['runs'],
                textposition='outside',
                marker=dict(
                    color=top_10['strike_rate'],
                    colorscale='Viridis',
                    colorbar=dict(title="Strike Rate"),
                    line=dict(color='white', width=1)
                ),
                hovertemplate='<b>%{x}</b><br>Runs: %{y}<br>Strike Rate: %{marker.color:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"Top 10 Run Scorers - {selected_team_batting}",
                xaxis_title="Batsman",
                yaxis_title="Runs",
                height=500,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="batting_top10_chart")
            
            # Strike Rate vs Average Chart
            st.markdown("---")
            st.markdown("#### 📊 Strike Rate vs Average")
            
            fig2 = go.Figure()
            
            # Filter batsmen with at least 50 balls for meaningful comparison
            comparison_df = batting_stats[batting_stats['balls'] >= 50].copy()
            
            if not comparison_df.empty:
                fig2.add_trace(go.Scatter(
                    x=comparison_df['average'],
                    y=comparison_df['strike_rate'],
                    mode='markers+text',
                    text=comparison_df['batsman'],
                    textposition='top center',
                    marker=dict(
                        size=comparison_df['runs'] / 10,  # Size based on runs
                        color=comparison_df['boundaries'],
                        colorscale='RdYlGn',
                        colorbar=dict(title="Boundaries"),
                        line=dict(color='white', width=1)
                    ),
                    hovertemplate='<b>%{text}</b><br>Average: %{x:.2f}<br>Strike Rate: %{y:.2f}<br>Runs: %{marker.size*10:.0f}<extra></extra>'
                ))
                
                # Add average lines
                avg_sr = comparison_df['strike_rate'].mean()
                avg_avg = comparison_df['average'].mean()
                
                fig2.add_hline(y=avg_sr, line_dash="dash", line_color="gray", annotation_text=f"Avg SR: {avg_sr:.1f}")
                fig2.add_vline(x=avg_avg, line_dash="dash", line_color="gray", annotation_text=f"Avg: {avg_avg:.1f}")
                
                fig2.update_layout(
                    title="Strike Rate vs Average (Min 50 balls)",
                    xaxis_title="Batting Average",
                    yaxis_title="Strike Rate",
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig2, use_container_width=True, key="batting_scatter_chart")
            else:
                st.info("Not enough data for comparison chart (minimum 50 balls required)")
            
        else:
            st.warning("⚠️ No batsmen with minimum 10 balls in selected filters")
    else:
        st.warning("⚠️ No data available for selected filters")


def render_bowling_stats(filtered_df):
    """Render detailed bowling statistics"""
    
    st.markdown("### 🎯 Bowling Statistics")
    
    # Sidebar filters for bowling
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Bowling Stats Filters")
    
    # Get bowling teams (opponent teams)
    filtered_df['bowling_team'] = filtered_df.apply(
        lambda row: row['team2_battingsecond'] if row['innings'] == 1 else row['team1_battingfirst'],
        axis=1
    )
    
    all_teams = sorted(filtered_df['bowling_team'].unique())
    
    # Team filter
    selected_team_bowling = st.sidebar.selectbox(
        "Select Team",
        options=all_teams,
        key="bowling_stats_team"
    )
    
    # Innings filter
    innings_option_bowl = st.sidebar.selectbox(
        "Select Innings",
        options=["Both Innings", "1st Innings", "2nd Innings"],
        key="bowling_stats_innings"
    )
    
    # Phase filter
    phase_option_bowl = st.sidebar.selectbox(
        "Select Phase",
        options=["Entire Innings", "Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"],
        key="bowling_stats_phase"
    )
    
    # Apply filters
    bowling_df = filtered_df[filtered_df['bowling_team'] == selected_team_bowling].copy()
    
    if innings_option_bowl == "1st Innings":
        bowling_df = bowling_df[bowling_df['innings'] == 1]
    elif innings_option_bowl == "2nd Innings":
        bowling_df = bowling_df[bowling_df['innings'] == 2]
    
    if phase_option_bowl != "Entire Innings":
        bowling_df = bowling_df[bowling_df['phase'] == phase_option_bowl]
    
    # Calculate bowling statistics
    if len(bowling_df) > 0:
        # Group by bowler
        bowling_stats = bowling_df.groupby('bowler').agg(
            runs_conceded=('total_runs', 'sum'),
            wickets=('is_wicket', 'sum'),
            balls_bowled=('ball', lambda x: len(x[bowling_df.loc[x.index, 'extras'] == 0])),  # Only legal deliveries
            dots=('runs_offbat', lambda x: (x == 0).sum()),
            fours_conceded=('runs_offbat', lambda x: (x == 4).sum()),
            sixes_conceded=('runs_offbat', lambda x: (x == 6).sum()),
            wides=('extra_type', lambda x: (x == 'Wide').sum()),
            noballs=('extra_type', lambda x: (x == 'NB').sum())
        ).reset_index()
        
        # Calculate overs (proper cricket format)
        def balls_to_overs(balls):
            complete_overs = balls // 6
            remaining_balls = balls % 6
            return complete_overs + (remaining_balls / 10)
        
        bowling_stats['overs'] = bowling_stats['balls_bowled'].apply(balls_to_overs).round(1)
        bowling_stats['economy'] = (bowling_stats['runs_conceded'] / (bowling_stats['balls_bowled'] / 6)).round(2)
        bowling_stats['average'] = (bowling_stats['runs_conceded'] / bowling_stats['wickets'].replace(0, 1)).round(2)
        bowling_stats['strike_rate'] = (bowling_stats['balls_bowled'] / bowling_stats['wickets'].replace(0, 1)).round(2)
        bowling_stats['dot_percentage'] = (bowling_stats['dots'] / bowling_stats['balls_bowled'] * 100).round(1)
        
        # Filter bowlers with minimum 12 balls (2 overs)
        bowling_stats = bowling_stats[bowling_stats['balls_bowled'] >= 12]
        
        if not bowling_stats.empty:
            # Sort by wickets
            bowling_stats = bowling_stats.sort_values('wickets', ascending=False).reset_index(drop=True)
            
            # Display title with filters
            st.markdown(f"#### 📊 {selected_team_bowling} - Bowling Statistics")
            st.markdown(f"*Filters: {innings_option_bowl} | {phase_option_bowl}*")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Wickets", f"{bowling_stats['wickets'].sum()}")
            with col2:
                st.metric("Runs Conceded", f"{bowling_stats['runs_conceded'].sum():,}")
            with col3:
                st.metric("Dot Balls", f"{bowling_stats['dots'].sum():,}")
            with col4:
                st.metric("Team Economy", f"{(bowling_stats['runs_conceded'].sum() / (bowling_stats['balls_bowled'].sum() / 6)):.2f}")
            
            st.markdown("---")
            
            # Display table
            display_stats = bowling_stats[[
                'bowler', 'overs', 'runs_conceded', 'wickets', 'economy',
                'average', 'strike_rate', 'dots', 'dot_percentage',
                'wides', 'noballs'
            ]].copy()
            
            # Rename columns for display
            display_stats.columns = [
                'Bowler', 'Overs', 'Runs', 'Wickets', 'Economy',
                'Average', 'Strike Rate', 'Dots', 'Dot %',
                'Wides', 'No Balls'
            ]
            
            # Style the dataframe
            st.dataframe(
                display_stats,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Visualization - Top 10 Wicket Takers
            st.markdown("---")
            st.markdown("#### 📈 Top 10 Wicket Takers")
            
            top_10_bowlers = bowling_stats.head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_10_bowlers['bowler'],
                y=top_10_bowlers['wickets'],
                text=top_10_bowlers['wickets'],
                textposition='outside',
                marker=dict(
                    color=top_10_bowlers['economy'],
                    colorscale='RdYlGn_r',  # Reverse scale (lower economy = better)
                    colorbar=dict(title="Economy"),
                    line=dict(color='white', width=1)
                ),
                hovertemplate='<b>%{x}</b><br>Wickets: %{y}<br>Economy: %{marker.color:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"Top 10 Wicket Takers - {selected_team_bowling}",
                xaxis_title="Bowler",
                yaxis_title="Wickets",
                height=500,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="bowling_top10_chart")
            
            # Economy vs Strike Rate Chart
            st.markdown("---")
            st.markdown("#### 📊 Economy vs Strike Rate")
            
            fig2 = go.Figure()
            
            # Filter bowlers with at least 4 overs for meaningful comparison
            comparison_df = bowling_stats[bowling_stats['balls_bowled'] >= 24].copy()
            
            if not comparison_df.empty:
                fig2.add_trace(go.Scatter(
                    x=comparison_df['strike_rate'],
                    y=comparison_df['economy'],
                    mode='markers+text',
                    text=comparison_df['bowler'],
                    textposition='top center',
                    marker=dict(
                        size=comparison_df['wickets'] * 5,  # Size based on wickets
                        color=comparison_df['dot_percentage'],
                        colorscale='Greens',
                        colorbar=dict(title="Dot %"),
                        line=dict(color='white', width=1)
                    ),
                    hovertemplate='<b>%{text}</b><br>Strike Rate: %{x:.2f}<br>Economy: %{y:.2f}<br>Wickets: %{marker.size/5:.0f}<extra></extra>'
                ))
                
                # Add average lines
                avg_sr_bowl = comparison_df['strike_rate'].mean()
                avg_econ = comparison_df['economy'].mean()
                
                fig2.add_hline(y=avg_econ, line_dash="dash", line_color="gray", annotation_text=f"Avg Economy: {avg_econ:.1f}")
                fig2.add_vline(x=avg_sr_bowl, line_dash="dash", line_color="gray", annotation_text=f"Avg SR: {avg_sr_bowl:.1f}")
                
                fig2.update_layout(
                    title="Economy vs Strike Rate (Min 4 overs)",
                    xaxis_title="Bowling Strike Rate (balls per wicket)",
                    yaxis_title="Economy Rate",
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig2, use_container_width=True, key="bowling_scatter_chart")
            else:
                st.info("Not enough data for comparison chart (minimum 4 overs required)")
            
        else:
            st.warning("⚠️ No bowlers with minimum 2 overs in selected filters")
    else:
        st.warning("⚠️ No data available for selected filters")
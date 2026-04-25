import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_bowling_dashboard(df, selected_teams, selected_matches):
    """
    Render the bowling analysis dashboard - Complete implementation
    Matches the original bowling.py with all charts
    """
    
    # Sidebar filters for this tab
    st.sidebar.markdown("### 🎯 Bowling Filters")
    
    phase_options = {
        "Entire Innings": (0, 20),
        "Powerplay (Overs 1-6)": (0, 5),
        "Middle Overs (7-15)": (6, 14),
        "Middle Overs 1 (7-10)": (6, 9),
        "Middle Overs 2 (11-15)": (10, 14),
        "Death Overs (16-20)": (15, 19)
    }
    selected_phase = st.sidebar.selectbox("🎯 Select Phase", list(phase_options.keys()), key="bowling_phase")
    
    innings_options = ["Both Innings", "1st Innings", "2nd Innings"]
    selected_innings = st.sidebar.radio("⚡ Select Innings", innings_options, key="bowling_innings")
    
    # Get all teams
    all_teams = sorted(set(df['team1_battingfirst'].unique().tolist() + df['team2_battingsecond'].unique().tolist()))
    selected_team = st.sidebar.selectbox("🏆 Select Team for Detailed Stats", ["All Teams"] + all_teams, key="bowling_team_detail")
    
    # Apply phase and innings filters
    filtered_df = df.copy()
    
    # Phase filter
    over_range = phase_options[selected_phase]
    filtered_df = filtered_df[(filtered_df['over'] >= over_range[0]) & (filtered_df['over'] <= over_range[1])]
    
    # Innings filter
    if selected_innings == "1st Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 1]
    elif selected_innings == "2nd Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 2]
    
    # Get bowling team
    def get_bowling_team(row):
        if row['innings'] == 1:
            return row['team2_battingsecond']
        else:
            return row['team1_battingfirst']
    
    filtered_df['bowling_team'] = filtered_df.apply(get_bowling_team, axis=1)
    
    # =========================
    # KEY METRICS
    # =========================
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_overs = len(filtered_df) / 6
        st.metric("Total Overs", f"{total_overs:.1f}")
    
    with col2:
        total_runs = filtered_df['runs_offbat'].sum() + filtered_df['extras'].sum()
        st.metric("Total Runs", total_runs)
    
    with col3:
        total_wickets = filtered_df['is_wicket'].sum()
        st.metric("Total Wickets", total_wickets)
    
    with col4:
        avg_economy = (total_runs / total_overs) if total_overs > 0 else 0
        st.metric("Average Economy", f"{avg_economy:.2f}")
    
    with col5:
        total_boundaries = filtered_df['is_boundary'].sum()
        st.metric("Total Boundaries", total_boundaries)
    
    st.markdown("---")
    
    # =========================
    # CHART 1: AVERAGE 1ST INNINGS SCORE CONCEDED
    # =========================
    st.subheader("📊 Average 1st Innings Score Conceded")
    
    first_innings_df = df[df['innings'] == 1]
    team_avg_runs = []
    
    for team in all_teams:
        team_bowling_df = first_innings_df.copy()
        team_bowling_df['bowling_team'] = team_bowling_df.apply(get_bowling_team, axis=1)
        team_specific = team_bowling_df[team_bowling_df['bowling_team'] == team]
        
        if len(team_specific) > 0:
            match_runs = team_specific.groupby('match_no').agg({
                'runs_offbat': 'sum',
                'extras': 'sum'
            })
            total_runs = match_runs['runs_offbat'] + match_runs['extras']
            avg_runs = total_runs.mean()
            num_matches = len(total_runs)
            
            league_avg = 156
            matches_above_avg = (total_runs > league_avg).sum()
            
            team_avg_runs.append({
                'Team': team,
                'Avg Runs Conceded': round(avg_runs, 0),
                'Matches': num_matches,
                'Matches Above 156': matches_above_avg
            })
    
    team_avg_df = pd.DataFrame(team_avg_runs).sort_values('Avg Runs Conceded')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig1 = go.Figure()
        
        colors = ['#5DADE2' if x < 156 else '#1F618D' for x in team_avg_df['Avg Runs Conceded']]
        
        fig1.add_trace(go.Bar(
            x=team_avg_df['Team'],
            y=team_avg_df['Avg Runs Conceded'],
            marker_color=colors,
            text=team_avg_df['Avg Runs Conceded'].astype(int),
            textposition='outside',
            textfont=dict(size=12, color='black')
        ))
        
        fig1.add_hline(y=156, line_dash="dash", line_color="red", 
                       annotation_text=f"Average: 156", annotation_position="right")
        
        fig1.update_layout(
            title="Average Runs Conceded in 1st Innings by Team",
            xaxis_title="Teams",
            yaxis_title="Average Runs Conceded",
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(240,240,240,0.5)',
            yaxis=dict(gridcolor='white')
        )
        
        st.plotly_chart(fig1, use_container_width=True, key="bowling_innings_comp_left")
    
    with col2:
        fig2 = go.Figure()
        
        colors_2 = ['#85C1E2' if i % 2 == 0 else '#5DADE2' for i in range(len(team_avg_df))]
        
        fig2.add_trace(go.Bar(
            y=team_avg_df['Team'],
            x=team_avg_df['Matches Above 156'],
            orientation='h',
            marker_color=colors_2,
            text=team_avg_df['Matches Above 156'],
            textposition='outside',
            textfont=dict(size=11)
        ))
        
        fig2.update_layout(
            title=f"Teams Conceding > 156 in 1st Innings",
            xaxis_title="# of Matches",
            yaxis_title="",
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(240,240,240,0.5)',
            xaxis=dict(gridcolor='white')
        )
        
        st.plotly_chart(fig2, use_container_width=True, key="bowling_innings_comp_right")
    
    st.markdown("---")
    
    # =========================
    # CHART 2: BOWLING COMPARISON ACROSS TEAMS
    # =========================
    st.subheader("🎯 Bowling Comparison Across Teams")
    
    team_bowling_comparison = []
    
    for team in all_teams:
        team_df = filtered_df.copy()
        team_df['bowling_team'] = team_df.apply(get_bowling_team, axis=1)
        team_specific = team_df[team_df['bowling_team'] == team]
        
        if len(team_specific) > 0:
            innings_count = len(team_specific['match_no'].unique())
            balls = len(team_specific)
            runs = team_specific['runs_offbat'].sum() + team_specific['extras'].sum()
            wickets = team_specific['is_wicket'].sum()
            overs = balls / 6
            
            economy = (runs / overs) if overs > 0 else 0
            avg_wickets = wickets / innings_count if innings_count > 0 else 0
            run_rate = economy
            dot_balls = len(team_specific[(team_specific['runs_offbat'] == 0) & (team_specific['extras'] == 0)])
            avg_dot_balls = dot_balls / innings_count if innings_count > 0 else 0
            
            team_bowling_comparison.append({
                'Team': team,
                'Innings': innings_count,  # Keep as int
                'Avg Wickets': avg_wickets,  # Will round in display
                'Economy': round(economy, 2),
                'Run Rate': round(run_rate, 1),  # Keep 1 decimal
                'Avg Dot Balls': avg_dot_balls  # Will round in display
            })
    
    comparison_df = pd.DataFrame(team_bowling_comparison)
    comparison_df = comparison_df.sort_values('Economy')
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Bar(
        name='# of Innings',
        x=comparison_df['Team'],
        y=comparison_df['Innings'],
        marker_color='#AED6F1',
        text=comparison_df['Innings'].astype(int),  # Round to int
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig3.add_trace(go.Bar(
        name='Avg Wickets',
        x=comparison_df['Team'],
        y=comparison_df['Avg Wickets'],
        marker_color='#F8B739',
        text=comparison_df['Avg Wickets'].round(0).astype(int),  # Round to whole number
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig3.add_trace(go.Bar(
        name='Run Rate',
        x=comparison_df['Team'],
        y=comparison_df['Run Rate'],
        marker_color='#A569BD',
        text=comparison_df['Run Rate'].round(1),  # Keep 1 decimal
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig3.add_trace(go.Bar(
        name='Avg Dot Balls',
        x=comparison_df['Team'],
        y=comparison_df['Avg Dot Balls'],
        marker_color='#D4E157',
        text=comparison_df['Avg Dot Balls'].round(0).astype(int),  # Round to whole number
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig3.update_layout(
        title="Bowling Comparison - Sorted by Economy (Lowest to Highest)",
        xaxis_title="Teams",
        yaxis_title="Value",
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(250,250,250,0.8)',
        yaxis=dict(gridcolor='white')
    )
    
    st.plotly_chart(fig3, use_container_width=True, key="bowling_wickets_phases")
    st.info("📝 **Note:** Graph sorted based on economy from lowest to highest")
    
    st.markdown("---")
    
    # =========================
    # CHART 3: SEAMERS & SPINNERS COMPARISON
    # =========================
    st.subheader("⚾ Seamers & Spinners Comparison")
    
    # Calculate TEAM-level stats for seamers and spinners
    team_bowler_stats = []
    
    for team in all_teams:
        team_df = filtered_df.copy()
        team_df['bowling_team'] = team_df.apply(get_bowling_team, axis=1)
        team_specific = team_df[team_df['bowling_team'] == team]
        
        if len(team_specific) > 0:
            # Seamers stats
            seamers_data = team_specific[team_specific['pace_or_spin'] == 'pace']
            if len(seamers_data) > 0:
                balls_pace = len(seamers_data)
                runs_pace = seamers_data['runs_offbat'].sum() + seamers_data['extras'].sum()
                overs_pace = balls_pace / 6
                economy_pace = (runs_pace / overs_pace) if overs_pace > 0 else 0
                
                team_bowler_stats.append({
                    'Team': team,
                    'Type': 'Seamers',
                    'Overs': round(overs_pace, 1),
                    'Economy': round(economy_pace, 2)
                })
            
            # Spinners stats  
            spinners_data = team_specific[team_specific['pace_or_spin'] == 'spin']
            if len(spinners_data) > 0:
                balls_spin = len(spinners_data)
                runs_spin = spinners_data['runs_offbat'].sum() + spinners_data['extras'].sum()
                overs_spin = balls_spin / 6
                economy_spin = (runs_spin / overs_spin) if overs_spin > 0 else 0
                
                team_bowler_stats.append({
                    'Team': team,
                    'Type': 'Spinners',
                    'Overs': round(overs_spin, 1),
                    'Economy': round(economy_spin, 2)
                })
    
    scatter_df = pd.DataFrame(team_bowler_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        seamers_df = scatter_df[scatter_df['Type'] == 'Seamers']
        
        if len(seamers_df) > 0:
            fig4 = go.Figure()
            
            avg_overs = seamers_df['Overs'].mean()
            avg_econ = seamers_df['Economy'].mean()
            
            fig4.add_trace(go.Scatter(
                x=seamers_df['Overs'],
                y=seamers_df['Economy'],
                mode='markers+text',
                marker=dict(size=14, color='#3498DB', symbol='star'),
                text=seamers_df['Team'],
                textposition='top center',
                textfont=dict(size=9),
                name='Seamers',
                hovertemplate='<b>%{text}</b><br>Overs: %{x}<br>Economy: %{y}<extra></extra>'
            ))
            
            fig4.add_hline(y=avg_econ, line_dash="dash", line_color="red",
                          annotation_text=f"Average = {avg_econ:.2f}")
            fig4.add_vline(x=avg_overs, line_dash="dash", line_color="gray",
                          annotation_text=f"Average = {avg_overs:.1f}")
            
            fig4.update_layout(
                title="Seamers Analysis",
                xaxis_title="Overs Bowled",
                yaxis_title="Economy Rate",
                height=450,
                plot_bgcolor='rgba(250,250,250,0.9)',
                xaxis=dict(gridcolor='white'),
                yaxis=dict(gridcolor='white')
            )
            
            st.plotly_chart(fig4, use_container_width=True, key="bowling_seamers_analysis")
            st.caption(f"📊 Showing {len(seamers_df)} teams")
    
    with col2:
        spinners_df = scatter_df[scatter_df['Type'] == 'Spinners']
        
        if len(spinners_df) > 0:
            fig5 = go.Figure()
            
            avg_overs_spin = spinners_df['Overs'].mean()
            avg_econ_spin = spinners_df['Economy'].mean()
            
            fig5.add_trace(go.Scatter(
                x=spinners_df['Overs'],
                y=spinners_df['Economy'],
                mode='markers+text',
                marker=dict(size=14, color='#E74C3C', symbol='star'),
                text=spinners_df['Team'],
                textposition='top center',
                textfont=dict(size=9),
                name='Spinners',
                hovertemplate='<b>%{text}</b><br>Overs: %{x}<br>Economy: %{y}<extra></extra>'
            ))
            
            fig5.add_hline(y=avg_econ_spin, line_dash="dash", line_color="red",
                          annotation_text=f"Average = {avg_econ_spin:.2f}")
            fig5.add_vline(x=avg_overs_spin, line_dash="dash", line_color="gray",
                          annotation_text=f"Average = {avg_overs_spin:.1f}")
            
            fig5.update_layout(
                title="Spinners Analysis",
                xaxis_title="Overs Bowled",
                yaxis_title="Economy Rate",
                height=450,
                plot_bgcolor='rgba(250,250,250,0.9)',
                xaxis=dict(gridcolor='white'),
                yaxis=dict(gridcolor='white')
            )
            
            st.plotly_chart(fig5, use_container_width=True, key="bowling_spinners_analysis")
            st.caption(f"📊 Showing {len(spinners_df)} teams")
    
    st.markdown("---")
    
    # =========================
    # CHART 4: OVERALL VS LHB & RHB
    # =========================
    st.subheader("🎭 Overall Performance vs LHB & RHB")
    
    team_vs_hand = []
    
    for team in all_teams:
        team_df = filtered_df.copy()
        team_df['bowling_team'] = team_df.apply(get_bowling_team, axis=1)
        team_specific = team_df[team_df['bowling_team'] == team]
        
        if len(team_specific) > 0:
            # vs Right-handed batsmen
            rhb_df = team_specific[team_specific['batting_hand'] == 'Right']
            if len(rhb_df) > 0:
                rhb_balls = len(rhb_df)
                rhb_runs = rhb_df['runs_offbat'].sum() + rhb_df['extras'].sum()
                rhb_overs = rhb_balls / 6
                rhb_economy = (rhb_runs / rhb_overs) if rhb_overs > 0 else 0
            else:
                rhb_economy = 0
            
            # vs Left-handed batsmen
            lhb_df = team_specific[team_specific['batting_hand'] == 'Left']
            if len(lhb_df) > 0:
                lhb_balls = len(lhb_df)
                lhb_runs = lhb_df['runs_offbat'].sum() + lhb_df['extras'].sum()
                lhb_overs = lhb_balls / 6
                lhb_economy = (lhb_runs / lhb_overs) if lhb_overs > 0 else 0
            else:
                lhb_economy = 0
            
            team_vs_hand.append({
                'Team': team,
                'RHB': round(rhb_economy, 2),
                'LHB': round(lhb_economy, 2)
            })
    
    vs_hand_df = pd.DataFrame(team_vs_hand)
    
    # Sort by RHB economy for better visualization
    vs_hand_df = vs_hand_df.sort_values('RHB')
    
    fig6 = go.Figure()
    
    # Use distinct colors for each team
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
    
    for idx, row in vs_hand_df.iterrows():
        color = colors[idx % len(colors)]
        fig6.add_trace(go.Scatter(
            x=['RHB', 'LHB'],
            y=[row['RHB'], row['LHB']],
            mode='lines+markers',
            name=row['Team'],
            line=dict(width=2.5, color=color),
            marker=dict(size=12, color=color),
            hovertemplate=f"<b>{row['Team']}</b><br>" + 
                         "RHB Economy: %{y:.2f}<extra></extra>"
        ))
    
    fig6.update_layout(
        title="Economy Rate: vs Right-Handed vs Left-Handed Batsmen",
        xaxis_title="Batsman Type",
        yaxis_title="Economy Rate (Runs per Over)",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        plot_bgcolor='white',
        yaxis=dict(gridcolor='lightgray', range=[0, max(vs_hand_df['RHB'].max(), vs_hand_df['LHB'].max()) * 1.1]),
        xaxis=dict(showgrid=False)
    )
    
    st.plotly_chart(fig6, use_container_width=True, key="bowling_overall_vs_lhb_rhb")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        best_vs_rhb = vs_hand_df.loc[vs_hand_df['RHB'].idxmin()]
        st.metric("Best vs RHB", f"{best_vs_rhb['Team']}", f"{best_vs_rhb['RHB']:.2f}")
    with col2:
        best_vs_lhb = vs_hand_df.loc[vs_hand_df['LHB'].idxmin()]
        st.metric("Best vs LHB", f"{best_vs_lhb['Team']}", f"{best_vs_lhb['LHB']:.2f}")
    with col3:
        avg_rhb = vs_hand_df['RHB'].mean()
        avg_lhb = vs_hand_df['LHB'].mean()
        st.metric("Avg Economy", "RHB vs LHB", f"{avg_rhb:.2f} vs {avg_lhb:.2f}")
    
    
    # =========================
    # DETAILED STATS: TEAM-WISE VS PACE/SPIN & PLAYER-WISE
    # =========================
    st.subheader("📋 Detailed Bowling Performance Analysis")
    
    # Helper function to convert balls to cricket overs format
    def balls_to_overs(balls):
        """Convert balls to cricket overs format (e.g., 10.3 = 10 overs 3 balls)"""
        if balls == 0:
            return 0.0
        complete_overs = balls // 6
        remaining_balls = balls % 6
        return float(f"{complete_overs}.{remaining_balls}")
    
    # Add filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        view_type = st.selectbox(
            "📊 View Type:",
            ["Team-wise Stats", "Player-wise Stats"],
            key="bowling_view_type"
        )
    
    with col_filter2:
        bowling_type_filter = st.selectbox(
            "🎯 Against Type:",
            ["Both", "Pace", "Spin"],
            key="bowling_type_filter"
        )
    
    st.markdown("---")
    
    # =============================
    # TEAM-WISE STATS AGAINST PACE/SPIN
    # =============================
    if view_type == "Team-wise Stats":
        st.markdown("### Team Performance Against Pace & Spin Bowlers")
        
        team_stats = []
        
        for team in all_teams:
            # Get team's batting data
            team_batting_df = filtered_df.copy()
            
            # Filter for this team as batting team
            def is_batting_team(row, team_name):
                if row['innings'] == 1:
                    return row['team1_battingfirst'] == team_name
                else:
                    return row['team2_battingsecond'] == team_name
            
            team_batting_df['is_target_team'] = team_batting_df.apply(lambda x: is_batting_team(x, team), axis=1)
            team_batting_df = team_batting_df[team_batting_df['is_target_team']]
            
            if len(team_batting_df) > 0:
                # Apply bowling type filter
                if bowling_type_filter == "Pace":
                    team_batting_df = team_batting_df[team_batting_df['pace_or_spin'] == 'pace']
                elif bowling_type_filter == "Spin":
                    team_batting_df = team_batting_df[team_batting_df['pace_or_spin'] == 'spin']
                
                if len(team_batting_df) > 0:
                    # Count only legal deliveries (extras = 0 for wides/no balls)
                    legal_balls = len(team_batting_df[team_batting_df['extras'] == 0])
                    total_runs = team_batting_df['runs_offbat'].sum() + team_batting_df['extras'].sum()
                    wickets = team_batting_df['is_wicket'].sum()
                    
                    overs = balls_to_overs(legal_balls)
                    overs_decimal = legal_balls / 6
                    economy = (total_runs / overs_decimal) if overs_decimal > 0 else 0
                    average = (total_runs / wickets) if wickets > 0 else total_runs
                    strike_rate = (legal_balls / wickets) if wickets > 0 else legal_balls
                    
                    team_stats.append({
                        'Team': team,
                        'Overs': overs,
                        'Runs': int(total_runs),  # Convert to integer
                        'Wickets': wickets,
                        'Economy': round(economy, 2),
                        'Average': round(average, 2),
                        'Strike Rate': round(strike_rate, 2)
                    })
        
        if team_stats:
            team_stats_df = pd.DataFrame(team_stats)
            team_stats_df = team_stats_df.sort_values('Economy')
            
            # Display with color coding
            st.dataframe(
                team_stats_df.style.background_gradient(subset=['Economy'], cmap='RdYlGn_r'),
                use_container_width=True,
                height=400
            )
            
            # Summary
            st.caption(f"📊 Showing {len(team_stats_df)} teams • Against: {bowling_type_filter}")
        else:
            st.warning("No data available for selected filters")
    
    # =============================
    # PLAYER-WISE STATS (ORIGINAL TABLE)
    # =============================
    else:  # Player-wise Stats
        st.markdown("### Individual Bowler Performance vs RHB & LHB")
        
        detailed_vs_hand = []
        
        for bowler in filtered_df['bowler'].unique():
            bowler_df = filtered_df[filtered_df['bowler'] == bowler]
            
            # Apply bowling type filter
            if bowling_type_filter != "Both":
                bowler_type = bowler_df['pace_or_spin'].iloc[0]
                if bowling_type_filter == "Pace" and bowler_type != "pace":
                    continue
                if bowling_type_filter == "Spin" and bowler_type != "spin":
                    continue
            
            # Count only legal deliveries
            legal_balls = len(bowler_df[bowler_df['extras'] == 0])
            total_runs = bowler_df['runs_offbat'].sum() + bowler_df['extras'].sum()
            total_wickets = bowler_df['is_wicket'].sum()
            total_overs = balls_to_overs(legal_balls)
            total_overs_decimal = legal_balls / 6
            overall_econ = (total_runs / total_overs_decimal) if total_overs_decimal > 0 else 0
            overall_avg = (total_runs / total_wickets) if total_wickets > 0 else total_runs
            overall_sr = (legal_balls / total_wickets) if total_wickets > 0 else legal_balls
            
            # vs RHB
            rhb_df = bowler_df[bowler_df['batting_hand'] == 'Right']
            if len(rhb_df) > 0:
                rhb_legal_balls = len(rhb_df[rhb_df['extras'] == 0])
                rhb_runs = rhb_df['runs_offbat'].sum() + rhb_df['extras'].sum()
                rhb_wickets = rhb_df['is_wicket'].sum()
                rhb_overs = balls_to_overs(rhb_legal_balls)
                rhb_overs_decimal = rhb_legal_balls / 6
                rhb_econ = (rhb_runs / rhb_overs_decimal) if rhb_overs_decimal > 0 else 0
                rhb_avg = (rhb_runs / rhb_wickets) if rhb_wickets > 0 else rhb_runs
                rhb_sr = (rhb_legal_balls / rhb_wickets) if rhb_wickets > 0 else rhb_legal_balls
            else:
                rhb_overs = rhb_runs = rhb_wickets = rhb_econ = rhb_avg = rhb_sr = 0
            
            # vs LHB
            lhb_df = bowler_df[bowler_df['batting_hand'] == 'Left']
            if len(lhb_df) > 0:
                lhb_legal_balls = len(lhb_df[lhb_df['extras'] == 0])
                lhb_runs = lhb_df['runs_offbat'].sum() + lhb_df['extras'].sum()
                lhb_wickets = lhb_df['is_wicket'].sum()
                lhb_overs = balls_to_overs(lhb_legal_balls)
                lhb_overs_decimal = lhb_legal_balls / 6
                lhb_econ = (lhb_runs / lhb_overs_decimal) if lhb_overs_decimal > 0 else 0
                lhb_avg = (lhb_runs / lhb_wickets) if lhb_wickets > 0 else lhb_runs
                lhb_sr = (lhb_legal_balls / lhb_wickets) if lhb_wickets > 0 else lhb_legal_balls
            else:
                lhb_overs = lhb_runs = lhb_wickets = lhb_econ = lhb_avg = lhb_sr = 0
            
            bowling_team = bowler_df['bowling_team'].iloc[0]
            pace_or_spin = bowler_df['pace_or_spin'].iloc[0]
            
            if legal_balls >= 6:  # Minimum 1 over bowled
                detailed_vs_hand.append({
                    'Bowler': bowler,
                    'Team': bowling_team,
                    'Type': pace_or_spin,
                    'Overall_Overs': total_overs,
                    'Overall_Runs': total_runs,
                    'Overall_Wkts': total_wickets,
                    'Overall_Econ': round(overall_econ, 2),
                    'Overall_Avg': round(overall_avg, 2),
                    'Overall_SR': round(overall_sr, 2),
                    'RHB_Overs': rhb_overs,
                    'RHB_Runs': rhb_runs,
                    'RHB_Wkts': rhb_wickets,
                    'RHB_Econ': round(rhb_econ, 2),
                    'RHB_Avg': round(rhb_avg, 2),
                    'RHB_SR': round(rhb_sr, 2),
                    'LHB_Overs': lhb_overs,
                    'LHB_Runs': lhb_runs,
                    'LHB_Wkts': lhb_wickets,
                    'LHB_Econ': round(lhb_econ, 2),
                    'LHB_Avg': round(lhb_avg, 2),
                    'LHB_SR': round(lhb_sr, 2)
                })
        
        if detailed_vs_hand:
            detailed_vs_hand_df = pd.DataFrame(detailed_vs_hand)
            
            tab1, tab2, tab3 = st.tabs(["📊 Overall Stats", "🎯 vs RHB", "🎯 vs LHB"])
            
            with tab1:
                st.markdown("### Overall Bowling Performance")
                overall_display = detailed_vs_hand_df[['Bowler', 'Team', 'Type', 'Overall_Overs', 
                                                        'Overall_Runs', 'Overall_Wkts', 'Overall_Econ', 
                                                        'Overall_Avg', 'Overall_SR']].copy()
                overall_display.columns = ['Bowler', 'Team', 'Type', 'Overs', 'Runs', 'Wickets', 
                                           'Economy', 'Average', 'Strike Rate']
                overall_display = overall_display.sort_values('Economy')
                st.dataframe(overall_display, use_container_width=True, height=400)
            
            with tab2:
                st.markdown("### Performance vs Right-Hand Batsmen")
                rhb_display = detailed_vs_hand_df[['Bowler', 'Team', 'Type', 'RHB_Overs', 
                                                    'RHB_Runs', 'RHB_Wkts', 'RHB_Econ', 
                                                    'RHB_Avg', 'RHB_SR']].copy()
                rhb_display.columns = ['Bowler', 'Team', 'Type', 'Overs', 'Runs', 'Wickets', 
                                       'Economy', 'Average', 'Strike Rate']
                rhb_display = rhb_display[rhb_display['Overs'] > 0].sort_values('Economy')
                st.dataframe(rhb_display, use_container_width=True, height=400)
            
            with tab3:
                st.markdown("### Performance vs Left-Hand Batsmen")
                lhb_display = detailed_vs_hand_df[['Bowler', 'Team', 'Type', 'LHB_Overs', 
                                                    'LHB_Runs', 'LHB_Wkts', 'LHB_Econ', 
                                                    'LHB_Avg', 'LHB_SR']].copy()
                lhb_display.columns = ['Bowler', 'Team', 'Type', 'Overs', 'Runs', 'Wickets', 
                                       'Economy', 'Average', 'Strike Rate']
                lhb_display = lhb_display[lhb_display['Overs'] > 0].sort_values('Economy')
                st.dataframe(lhb_display, use_container_width=True, height=400)
            
            st.caption(f"📊 Showing {len(detailed_vs_hand_df)} bowlers • Type: {bowling_type_filter}")
        else:
            st.warning("No bowlers found for selected filters")
    
    st.markdown("---")
    
    # =========================
    # CHART 5: SEAMERS & SPINNERS VS LHB & RHB
    # =========================
    st.subheader("⚡ Seamers & Spinners vs LHB & RHB")
    
    type_vs_hand = []
    
    for team in all_teams:
        team_df = filtered_df.copy()
        team_df['bowling_team'] = team_df.apply(get_bowling_team, axis=1)
        team_specific = team_df[team_df['bowling_team'] == team]
        
        # Seamers
        seamers_df = team_specific[team_specific['pace_or_spin'] == 'pace']
        seamers_rhb = seamers_df[seamers_df['batting_hand'] == 'Right']
        seamers_lhb = seamers_df[seamers_df['batting_hand'] == 'Left']
        
        seamer_rhb_score = len(seamers_rhb) / 6 if len(seamers_rhb) > 0 else 0
        seamer_lhb_score = len(seamers_lhb) / 6 if len(seamers_lhb) > 0 else 0
        
        # Spinners
        spinners_df = team_specific[team_specific['pace_or_spin'] == 'spin']
        spinners_rhb = spinners_df[spinners_df['batting_hand'] == 'Right']
        spinners_lhb = spinners_df[spinners_df['batting_hand'] == 'Left']
        
        spinner_rhb_score = len(spinners_rhb) / 6 if len(spinners_rhb) > 0 else 0
        spinner_lhb_score = len(spinners_lhb) / 6 if len(spinners_lhb) > 0 else 0
        
        type_vs_hand.append({
            'Team': team,
            'Seamer_RHB': round(seamer_rhb_score, 1),
            'Seamer_LHB': round(seamer_lhb_score, 1),
            'Spinner_RHB': round(spinner_rhb_score, 1),
            'Spinner_LHB': round(spinner_lhb_score, 1)
        })
    
    type_vs_hand_df = pd.DataFrame(type_vs_hand)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig7 = go.Figure()
        
        for idx, row in type_vs_hand_df.iterrows():
            if row['Seamer_RHB'] > 0 or row['Seamer_LHB'] > 0:
                fig7.add_trace(go.Scatter(
                    x=['RHB', 'LHB'],
                    y=[row['Seamer_RHB'], row['Seamer_LHB']],
                    mode='lines+markers+text',
                    name=row['Team'],
                    line=dict(width=2),
                    marker=dict(size=10),
                    text=[str(row['Seamer_RHB']), str(row['Seamer_LHB'])],
                    textposition='top center'
                ))
        
        fig7.update_layout(
            title="Seamers Performance vs RHB & LHB",
            xaxis_title="Batsman Type",
            yaxis_title="Score (in Overs)",
            height=450,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            plot_bgcolor='rgba(250,250,250,0.9)',
            yaxis=dict(gridcolor='white')
        )
        
        st.plotly_chart(fig7, use_container_width=True, key="bowling_seamers_vs_hand_left")
    
    with col2:
        fig8 = go.Figure()
        
        for idx, row in type_vs_hand_df.iterrows():
            if row['Spinner_RHB'] > 0 or row['Spinner_LHB'] > 0:
                fig8.add_trace(go.Scatter(
                    x=['RHB', 'LHB'],
                    y=[row['Spinner_RHB'], row['Spinner_LHB']],
                    mode='lines+markers+text',
                    name=row['Team'],
                    line=dict(width=2),
                    marker=dict(size=10),
                    text=[str(row['Spinner_RHB']), str(row['Spinner_LHB'])],
                    textposition='top center'
                ))
        
        fig8.update_layout(
            title="Spinners Performance vs RHB & LHB",
            xaxis_title="Batsman Type",
            yaxis_title="Score (in Overs)",
            height=450,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            plot_bgcolor='rgba(250,250,250,0.9)',
            yaxis=dict(gridcolor='white')
        )
        
        st.plotly_chart(fig8, use_container_width=True, key="bowling_spinners_vs_hand_right")
    
    st.info("""
    **Key Takeaways:**
    - The IDTT Spinners have the worst economy against RHB.
    - The IDTT Seamers have the worst bowling economy vs both RHB and LHB.
    """)
    
    st.markdown("---")
    
    # =========================
    # TEAM-SPECIFIC DETAILED STATS
    # =========================
    if selected_team != "All Teams":
        st.subheader(f"📊 Detailed Bowling Statistics - {selected_team}")
        
        # Calculate bowling stats
        bowling_stats = []
        
        for bowler in filtered_df['bowler'].unique():
            bowler_df = filtered_df[filtered_df['bowler'] == bowler]
            
            balls = len(bowler_df)
            runs = bowler_df['runs_offbat'].sum() + bowler_df['extras'].sum()
            wickets = bowler_df['is_wicket'].sum()
            overs = balls / 6
            
            economy = (runs / overs) if overs > 0 else 0
            avg = (runs / wickets) if wickets > 0 else runs if runs > 0 else 0
            sr = (balls / wickets) if wickets > 0 else balls if balls > 0 else 0
            
            bowling_hand = bowler_df['bowling_hand'].iloc[0]
            bowling_type = bowler_df['bowling_type'].iloc[0]
            pace_or_spin = bowler_df['pace_or_spin'].iloc[0]
            bowling_team = bowler_df['bowling_team'].iloc[0]
            
            dot_balls = len(bowler_df[(bowler_df['runs_offbat'] == 0) & (bowler_df['extras'] == 0)])
            boundaries = bowler_df['is_boundary'].sum()
            fours = len(bowler_df[(bowler_df['runs_offbat'] == 4) & (bowler_df['is_boundary'] == True)])
            sixes = len(bowler_df[(bowler_df['runs_offbat'] == 6) & (bowler_df['is_boundary'] == True)])
            
            bowling_stats.append({
                'Bowler': bowler,
                'Team': bowling_team,
                'Bowling Hand': bowling_hand,
                'Bowling Type': bowling_type,
                'Pace/Spin': pace_or_spin,
                'Innings': len(bowler_df['match_no'].unique()),
                'Overs': round(overs, 1),
                'Balls': balls,
                'Runs': runs,
                'Wickets': wickets,
                'Economy': round(economy, 2),
                'Average': round(avg, 2),
                'Strike Rate': round(sr, 2),
                'Dot Balls': dot_balls,
                '4s': fours,
                '6s': sixes,
                'Boundaries': boundaries
            })
        
        bowling_stats_df = pd.DataFrame(bowling_stats)
        team_bowlers = bowling_stats_df[bowling_stats_df['Team'] == selected_team].copy()
        team_bowlers = team_bowlers.sort_values('Economy')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_team_wickets = team_bowlers['Wickets'].sum()
            st.metric("Total Wickets", total_team_wickets)
        
        with col2:
            avg_team_economy = team_bowlers['Economy'].mean()
            st.metric("Average Economy", f"{avg_team_economy:.2f}")
        
        with col3:
            total_team_overs = team_bowlers['Overs'].sum()
            st.metric("Total Overs", f"{total_team_overs:.1f}")
        
        with col4:
            total_dot_balls = team_bowlers['Dot Balls'].sum()
            st.metric("Total Dot Balls", total_dot_balls)
        
        st.markdown("---")
        
        st.dataframe(
            team_bowlers[['Bowler', 'Bowling Type', 'Pace/Spin', 'Innings', 'Overs', 'Balls', 
                          'Runs', 'Wickets', 'Economy', 'Average', 'Strike Rate', 
                          'Dot Balls', '4s', '6s']],
            use_container_width=True,
            height=400
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_team1 = go.Figure()
            fig_team1.add_trace(go.Bar(
                x=team_bowlers['Bowler'],
                y=team_bowlers['Economy'],
                marker_color='#3498DB',
                text=team_bowlers['Economy'],
                textposition='outside'
            ))
            fig_team1.update_layout(
                title=f"Economy Rate - {selected_team}",
                xaxis_title="Bowler",
                yaxis_title="Economy",
                height=400,
                plot_bgcolor='rgba(250,250,250,0.9)'
            )
            st.plotly_chart(fig_team1, use_container_width=True, key="bowling_team_pace_chart")
        
        with col2:
            fig_team2 = go.Figure()
            fig_team2.add_trace(go.Bar(
                x=team_bowlers['Bowler'],
                y=team_bowlers['Wickets'],
                marker_color='#E74C3C',
                text=team_bowlers['Wickets'],
                textposition='outside'
            ))
            fig_team2.update_layout(
                title=f"Wickets Taken - {selected_team}",
                xaxis_title="Bowler",
                yaxis_title="Wickets",
                height=400,
                plot_bgcolor='rgba(250,250,250,0.9)'
            )
            st.plotly_chart(fig_team2, use_container_width=True, key="bowling_team_spin_chart")
    
    else:
        st.subheader("📊 All Teams Bowling Summary")
        
        # Calculate bowling stats for all bowlers
        bowling_stats = []
        
        for bowler in filtered_df['bowler'].unique():
            bowler_df = filtered_df[filtered_df['bowler'] == bowler]
            
            balls = len(bowler_df)
            runs = bowler_df['runs_offbat'].sum() + bowler_df['extras'].sum()
            wickets = bowler_df['is_wicket'].sum()
            overs = balls / 6
            
            economy = (runs / overs) if overs > 0 else 0
            bowling_team = bowler_df['bowling_team'].iloc[0]
            
            bowling_stats.append({
                'Bowler': bowler,
                'Team': bowling_team,
                'Overs': round(overs, 1),
                'Runs': runs,
                'Wickets': wickets,
                'Economy': round(economy, 2)
            })
        
        bowling_stats_df = pd.DataFrame(bowling_stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top 10 Bowlers by Economy")
            top_economy = bowling_stats_df[bowling_stats_df['Overs'] >= 2].nsmallest(10, 'Economy')
            st.dataframe(
                top_economy[['Bowler', 'Team', 'Overs', 'Runs', 'Wickets', 'Economy']],
                use_container_width=True,
                height=350
            )
        
        with col2:
            st.markdown("#### 🎯 Top 10 Wicket Takers")
            top_wickets = bowling_stats_df.nlargest(10, 'Wickets')
            st.dataframe(
                top_wickets[['Bowler', 'Team', 'Overs', 'Runs', 'Wickets', 'Economy']],
                use_container_width=True,
                height=350
            )
    
    st.markdown("---")
    
    # =========================
    # NEW TABLE: TEAM BOWLING PERFORMANCE VS RHB/LHB
    # =========================
    st.subheader("📊 Team Bowling Performance vs Right/Left Hand Batsmen")
    
    # Helper function to convert balls to cricket overs format
    def balls_to_overs_format(balls):
        """Convert balls to cricket overs format (e.g., 10.3 = 10 overs 3 balls)"""
        if balls == 0:
            return 0.0
        complete_overs = balls // 6
        remaining_balls = balls % 6
        return float(f"{complete_overs}.{remaining_balls}")
    
    # Filters
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        bowler_type_filter = st.selectbox(
            "🎳 Bowler Type:",
            ["Both", "Pace", "Spin"],
            key="team_bowling_perf_bowler_type"
        )
    
    with col_f2:
        batsman_type_filter = st.selectbox(
            "🏏 Batsman Type:",
            ["Both", "RHB", "LHB"],
            key="team_bowling_perf_batsman_type"
        )
    
    st.markdown("---")
    
    # Calculate team bowling performance
    team_bowling_performance = []
    
    for team in all_teams:
        # Get bowling data for this team
        team_bowling_df = filtered_df.copy()
        team_bowling_df['bowling_team'] = team_bowling_df.apply(get_bowling_team, axis=1)
        team_bowling_df = team_bowling_df[team_bowling_df['bowling_team'] == team]
        
        if len(team_bowling_df) > 0:
            # Apply bowler type filter
            if bowler_type_filter == "Pace":
                team_bowling_df = team_bowling_df[team_bowling_df['pace_or_spin'] == 'pace']
            elif bowler_type_filter == "Spin":
                team_bowling_df = team_bowling_df[team_bowling_df['pace_or_spin'] == 'spin']
            
            # Apply batsman type filter
            if batsman_type_filter == "RHB":
                team_bowling_df = team_bowling_df[team_bowling_df['batting_hand'] == 'Right']
            elif batsman_type_filter == "LHB":
                team_bowling_df = team_bowling_df[team_bowling_df['batting_hand'] == 'Left']
            
            if len(team_bowling_df) > 0:
                # Count only legal deliveries (exclude extras like wides and no balls)
                legal_balls = len(team_bowling_df[team_bowling_df['extras'] == 0])
                total_runs = team_bowling_df['runs_offbat'].sum() + team_bowling_df['extras'].sum()
                total_wickets = team_bowling_df['is_wicket'].sum()
                
                # Convert to overs
                overs_display = balls_to_overs_format(legal_balls)
                overs_decimal = legal_balls / 6  # For calculations
                
                # Calculate metrics
                economy = (total_runs / overs_decimal) if overs_decimal > 0 else 0
                average = (total_runs / total_wickets) if total_wickets > 0 else 0
                strike_rate = (legal_balls / total_wickets) if total_wickets > 0 else 0
                
                team_bowling_performance.append({
                    'Team': team,
                    'Overs': round(overs_display, 1),  # 1 decimal place
                    'Runs': int(total_runs),  # Integer
                    'Wickets': int(total_wickets),  # Integer
                    'Economy': round(economy, 2),  # 2 decimal places
                    'Average': round(average, 2),  # 2 decimal places
                    'Strike Rate': round(strike_rate, 2)  # 2 decimal places
                })
    
    if team_bowling_performance:
        team_bowling_perf_df = pd.DataFrame(team_bowling_performance)
        team_bowling_perf_df = team_bowling_perf_df.sort_values('Economy')
        
        # Format the display with exact decimal places
        styled_df = team_bowling_perf_df.style.format({
            'Overs': '{:.1f}',           # 1 decimal: 52.4
            'Runs': '{:.0f}',            # Integer: 431
            'Wickets': '{:.0f}',         # Integer: 26
            'Economy': '{:.2f}',         # 2 decimals: 8.18
            'Average': '{:.2f}',         # 2 decimals: 16.58
            'Strike Rate': '{:.2f}'      # 2 decimals: 12.15
        }).background_gradient(subset=['Economy'], cmap='RdYlGn_r')
        
        # Display with color gradient on Economy
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400
        )
        
        # Summary caption
        bowler_desc = bowler_type_filter if bowler_type_filter != "Both" else "All bowlers"
        batsman_desc = batsman_type_filter if batsman_type_filter != "Both" else "All batsmen"
        st.caption(f"📊 Showing: {bowler_desc} performance vs {batsman_desc} • Total teams: {len(team_bowling_perf_df)}")
    else:
        st.warning("⚠️ No data available for the selected filters")
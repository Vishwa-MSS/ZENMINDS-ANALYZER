import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_partnerships_dashboard(df, selected_teams, selected_matches):
    """
    Render the batting partnerships analysis dashboard
    Complete implementation with position-wise stats and partnership analysis
    Works WITHOUT non_striker column by tracking wickets
    """
    
    st.sidebar.markdown("### 🎯 Partnership Filters")
    
    phase_options = ["Entire Innings", "Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]
    selected_phase = st.sidebar.selectbox("Select Phase", phase_options, key="partnerships_phase_select")
    
    innings_options = ["Both Innings", "1st Innings", "2nd Innings"]
    selected_innings = st.sidebar.selectbox("Select Innings", innings_options, key="partnerships_innings_select")
    
    # Get all teams
    all_teams = sorted(set(df['team1_battingfirst'].unique().tolist() + df['team2_battingsecond'].unique().tolist()))
    
    # Team selector for comparison
    comparison_team = st.sidebar.selectbox(
        "Select Team for Comparison",
        ["Overall APL"] + all_teams,
        key="partnerships_team_comparison"
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Phase filter
    if selected_phase == "Powerplay (1-6)":
        filtered_df = filtered_df[filtered_df['over'] < 6]
    elif selected_phase == "Middle Overs (7-15)":
        filtered_df = filtered_df[(filtered_df['over'] >= 6) & (filtered_df['over'] < 16)]
    elif selected_phase == "Death Overs (16-20)":
        filtered_df = filtered_df[filtered_df['over'] >= 16]
    
    # Innings filter
    if selected_innings == "1st Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 1]
    elif selected_innings == "2nd Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 2]
    
    # Get batting team
    def get_batting_team(row):
        if row['innings'] == 1:
            return row['team1_battingfirst']
        else:
            return row['team2_battingsecond']
    
    filtered_df['batting_team'] = filtered_df.apply(get_batting_team, axis=1)
    
    # Calculate batting positions
    def calculate_batting_positions(data):
        """Calculate batting position for each batsman based on first appearance"""
        position_data = []
        
        for (match, inning), group in data.groupby(['match_no', 'innings']):
            first_appearance = {}
            
            for idx, row in group.sort_values(['over', 'ball']).iterrows():
                batsman = row['batsman']
                
                if batsman not in first_appearance:
                    first_appearance[batsman] = len(first_appearance) + 1
            
            for idx, row in group.iterrows():
                position_data.append({
                    'match_no': match,
                    'innings': inning,
                    'batsman': row['batsman'],
                    'batting_position': first_appearance.get(row['batsman'], 99),
                    'runs_offbat': row['runs_offbat'],
                    'ball': 1,
                    'batting_team': row['batting_team']
                })
        
        return pd.DataFrame(position_data)
    
    position_df = calculate_batting_positions(filtered_df)
    
    # CHART 1: BATTING POSITION WISE STATS - AVG RUNS
    st.subheader("📊 Batting Position Wise Stats - Average Runs")
    
    def calculate_position_stats(data, team_name=None):
        if team_name and team_name != "Overall APL":
            data = data[data['batting_team'] == team_name]
        
        stats = []
        for pos in range(1, 10):
            pos_data = data[data['batting_position'] == pos]
            
            if len(pos_data) > 0:
                innings_count = pos_data.groupby(['match_no', 'innings']).ngroups
                total_runs = pos_data['runs_offbat'].sum()
                total_balls = pos_data['ball'].sum()
                
                avg_runs = total_runs / innings_count if innings_count > 0 else 0
                avg_balls = total_balls / innings_count if innings_count > 0 else 0
                
                stats.append({
                    'Position': pos,
                    'Avg Runs': round(avg_runs, 0),
                    'Avg Balls': round(avg_balls, 0),
                    'Innings': innings_count
                })
        
        return pd.DataFrame(stats)
    
    overall_stats = calculate_position_stats(position_df, None)
    comparison_stats = calculate_position_stats(position_df, comparison_team if comparison_team != "Overall APL" else None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Overall APL")
        st.markdown("**AVG RUNS VS AVG BALLS FACED**")
        
        if not overall_stats.empty:
            fig1 = go.Figure()
            
            fig1.add_trace(go.Bar(
                y=overall_stats['Position'],
                x=overall_stats['Avg Runs'],
                orientation='h',
                name='Avg Runs per innings',
                marker=dict(color='#C88B8B'),
                text=overall_stats['Avg Runs'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig1.add_trace(go.Bar(
                y=overall_stats['Position'],
                x=overall_stats['Avg Balls'],
                orientation='h',
                name='Avg Balls per innings',
                marker=dict(color='#7DB4B5'),
                text=overall_stats['Avg Balls'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig1.add_trace(go.Bar(
                y=overall_stats['Position'],
                x=overall_stats['Innings'],
                orientation='h',
                name='# of Innings',
                marker=dict(color='#F4BE7A'),
                text=overall_stats['Innings'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig1.update_layout(
                barmode='group',
                height=500,
                yaxis=dict(tickmode='linear', tick0=1, dtick=1, title='', autorange='reversed'),
                xaxis=dict(
                    title='', 
                    showgrid=False,
                    range=[0, max(overall_stats['Innings'].max(), overall_stats['Avg Runs'].max(), overall_stats['Avg Balls'].max()) * 1.12]
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                plot_bgcolor='white',
                showlegend=True,
                margin=dict(l=50, r=60, t=60, b=40)
            )
            
            st.plotly_chart(fig1, use_container_width=True, key="partnerships_avg_runs_overall")
    
    with col2:
        st.markdown(f"### {comparison_team}")
        st.markdown("**AVG RUNS VS AVG BALLS FACED**")
        
        if not comparison_stats.empty:
            fig2 = go.Figure()
            
            fig2.add_trace(go.Bar(
                y=comparison_stats['Position'],
                x=comparison_stats['Avg Runs'],
                orientation='h',
                name='Avg Runs per innings',
                marker=dict(color='#C88B8B'),
                text=comparison_stats['Avg Runs'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig2.add_trace(go.Bar(
                y=comparison_stats['Position'],
                x=comparison_stats['Avg Balls'],
                orientation='h',
                name='Avg Balls per innings',
                marker=dict(color='#7DB4B5'),
                text=comparison_stats['Avg Balls'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig2.add_trace(go.Bar(
                y=comparison_stats['Position'],
                x=comparison_stats['Innings'],
                orientation='h',
                name='# of Innings',
                marker=dict(color='#F4BE7A'),
                text=comparison_stats['Innings'].astype(int),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig2.update_layout(
                barmode='group',
                height=500,
                yaxis=dict(tickmode='linear', tick0=1, dtick=1, title='', autorange='reversed'),
                xaxis=dict(
                    title='', 
                    showgrid=False,
                    range=[0, max(comparison_stats['Innings'].max(), comparison_stats['Avg Runs'].max(), comparison_stats['Avg Balls'].max()) * 1.12]
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                plot_bgcolor='white',
                showlegend=True,
                margin=dict(l=50, r=60, t=60, b=40)
            )
            
            st.plotly_chart(fig2, use_container_width=True, key="partnerships_avg_runs_team")
    
    if not overall_stats.empty:
        middle_order_avg = overall_stats[overall_stats['Position'].between(4, 7)]['Avg Runs'].mean()
        overall_avg = overall_stats['Avg Runs'].mean()
        
        if middle_order_avg < overall_avg:
            st.info(f"**Key takeaway:** The average runs scored by the middle order is below average ({middle_order_avg:.0f} vs {overall_avg:.0f}).")
    
    st.markdown("---")
    
    # CHART 2: STRIKE RATE
    st.subheader("📊 Batting Position Wise Stats - Strike Rate")
    
    def calculate_strike_rates(data, team_name=None):
        if team_name and team_name != "Overall APL":
            data = data[data['batting_team'] == team_name]
        
        stats = []
        for pos in range(1, 10):
            pos_data = data[data['batting_position'] == pos]
            
            if len(pos_data) > 0:
                total_runs = pos_data['runs_offbat'].sum()
                total_balls = pos_data['ball'].sum()
                
                strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0
                
                stats.append({
                    'Position': pos,
                    'Strike Rate': round(strike_rate, 2)
                })
        
        return pd.DataFrame(stats)
    
    overall_sr = calculate_strike_rates(position_df, None)
    comparison_sr = calculate_strike_rates(position_df, comparison_team if comparison_team != "Overall APL" else None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Overall APL")
        st.markdown("**STRIKE RATE**")
        
        if not overall_sr.empty:
            fig3 = go.Figure()
            
            fig3.add_trace(go.Bar(
                y=overall_sr['Position'],
                x=overall_sr['Strike Rate'],
                orientation='h',
                marker=dict(color='#5B9BD5'),
                text=overall_sr['Strike Rate'].round(1),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig3.update_layout(
                height=500,
                yaxis=dict(tickmode='linear', tick0=1, dtick=1, title='', autorange='reversed'),
                xaxis=dict(
                    title='', 
                    showgrid=False,
                    range=[0, overall_sr['Strike Rate'].max() * 1.12]
                ),
                plot_bgcolor='white',
                showlegend=False,
                margin=dict(l=50, r=60, t=60, b=40)
            )
            
            st.plotly_chart(fig3, use_container_width=True, key="partnerships_strike_rate_overall")
    
    with col2:
        st.markdown(f"### {comparison_team}")
        st.markdown("**STRIKE RATE**")
        
        if not comparison_sr.empty:
            fig4 = go.Figure()
            
            fig4.add_trace(go.Bar(
                y=comparison_sr['Position'],
                x=comparison_sr['Strike Rate'],
                orientation='h',
                marker=dict(color='#5B9BD5'),
                text=comparison_sr['Strike Rate'].round(1),
                textposition='outside',
                textfont=dict(color='#000', size=12, family='Arial Black')
            ))
            
            fig4.update_layout(
                height=500,
                yaxis=dict(tickmode='linear', tick0=1, dtick=1, title='', autorange='reversed'),
                xaxis=dict(
                    title='', 
                    showgrid=False,
                    range=[0, comparison_sr['Strike Rate'].max() * 1.12]
                ),
                plot_bgcolor='white',
                showlegend=False,
                margin=dict(l=50, r=60, t=60, b=40)
            )
            
            st.plotly_chart(fig4, use_container_width=True, key="partnerships_strike_rate_team")
    
    if not overall_sr.empty:
        top_order_sr = overall_sr[overall_sr['Position'] <= 3]['Strike Rate'].mean()
        overall_avg_sr = overall_sr['Strike Rate'].mean()
        
        if top_order_sr < overall_avg_sr:
            st.info(f"**Key takeaway:** The top order has a below average strike rate ({top_order_sr:.1f} vs {overall_avg_sr:.1f}), which is responsible for slow starts.")
    
    st.markdown("---")
    
    # CHART 3: PARTNERSHIPS
    st.subheader("🤝 Batting Partnerships Team Wise")
    
    def calculate_partnerships(data):
        partnerships = []
        
        for (match, inning), group in data.groupby(['match_no', 'innings']):
            group = group.sort_values(['over', 'ball']).reset_index(drop=True)
            
            partnership_runs = 0
            partnership_balls = 0
            wicket_count = 0
            
            for idx, row in group.iterrows():
                partnership_runs += row['runs_offbat']
                partnership_balls += 1
                
                if row['is_wicket']:
                    if partnership_balls > 0:
                        partnerships.append({
                            'match_no': match,
                            'innings': inning,
                            'batting_team': row['batting_team'],
                            'wicket': wicket_count + 1,
                            'runs': partnership_runs,
                            'balls': partnership_balls
                        })
                    
                    partnership_runs = 0
                    partnership_balls = 0
                    wicket_count += 1
            
            if partnership_balls > 0:
                partnerships.append({
                    'match_no': match,
                    'innings': inning,
                    'batting_team': group['batting_team'].iloc[-1],
                    'wicket': wicket_count + 1,
                    'runs': partnership_runs,
                    'balls': partnership_balls
                })
        
        return pd.DataFrame(partnerships)
    
    partnerships_df = calculate_partnerships(filtered_df)
    
    if not partnerships_df.empty:
        def calculate_team_partnerships(data, teams):
            results = []
            
            for team in teams:
                team_data = data[data['batting_team'] == team]
                
                count_30_plus = len(team_data[team_data['runs'] >= 30])
                count_50_plus = len(team_data[team_data['runs'] >= 50])
                count_100_plus = len(team_data[team_data['runs'] >= 100])
                
                highest = team_data['runs'].max() if len(team_data) > 0 else 0
                
                results.append({
                    'Team': team,
                    '30+': count_30_plus,
                    '50+': count_50_plus,
                    '100+': count_100_plus,
                    'High P\'ship': int(highest)
                })
            
            return pd.DataFrame(results)
        
        top_order_partnerships = partnerships_df[partnerships_df['wicket'] <= 3]
        middle_order_partnerships = partnerships_df[(partnerships_df['wicket'] >= 4) & (partnerships_df['wicket'] <= 7)]
        
        st.markdown("### Top Order")
        
        team_stats_top = calculate_team_partnerships(top_order_partnerships, all_teams)
        
        if not team_stats_top.empty:
            fig5 = go.Figure()
            
            x_labels = team_stats_top['Team'].tolist()
            
            fig5.add_trace(go.Bar(x=x_labels, y=team_stats_top['30+'], name='30+', text=team_stats_top['30+'], textposition='outside', marker=dict(color='#E8B4B8')))
            fig5.add_trace(go.Bar(x=x_labels, y=team_stats_top['50+'], name='50+', text=team_stats_top['50+'], textposition='outside', marker=dict(color='#A8D5BA')))
            fig5.add_trace(go.Bar(x=x_labels, y=team_stats_top['100+'], name='100+', text=team_stats_top['100+'], textposition='outside', marker=dict(color='#FFD9A0')))
            fig5.add_trace(go.Bar(x=x_labels, y=team_stats_top['High P\'ship'], name='High P\'ship', text=team_stats_top['High P\'ship'], textposition='outside', marker=dict(color='#FFB6C1')))
            
            fig5.update_layout(barmode='group', height=400, xaxis=dict(title='', tickangle=-45), yaxis=dict(title='', showgrid=False), legend=dict(orientation='h', y=1.02, x=1, xanchor='right', yanchor='bottom'), plot_bgcolor='white', margin=dict(l=50, r=20, t=60, b=120))
            
            st.plotly_chart(fig5, use_container_width=True, key="partnerships_breakdown_overall")
        
        st.markdown("### Middle Order")
        
        team_stats_middle = calculate_team_partnerships(middle_order_partnerships, all_teams)
        
        if not team_stats_middle.empty:
            fig6 = go.Figure()
            
            x_labels = team_stats_middle['Team'].tolist()
            
            fig6.add_trace(go.Bar(x=x_labels, y=team_stats_middle['30+'], name='30+', text=team_stats_middle['30+'], textposition='outside', marker=dict(color='#E8B4B8')))
            fig6.add_trace(go.Bar(x=x_labels, y=team_stats_middle['50+'], name='50+', text=team_stats_middle['50+'], textposition='outside', marker=dict(color='#A8D5BA')))
            fig6.add_trace(go.Bar(x=x_labels, y=team_stats_middle['100+'], name='100+', text=team_stats_middle['100+'], textposition='outside', marker=dict(color='#FFD9A0')))
            fig6.add_trace(go.Bar(x=x_labels, y=team_stats_middle['High P\'ship'], name='High P\'ship', text=team_stats_middle['High P\'ship'], textposition='outside', marker=dict(color='#FFB6C1')))
            
            fig6.update_layout(barmode='group', height=400, xaxis=dict(title='', tickangle=-45), yaxis=dict(title='', showgrid=False), legend=dict(orientation='h', y=1.02, x=1, xanchor='right', yanchor='bottom'), plot_bgcolor='white', margin=dict(l=50, r=20, t=60, b=120))
            
            st.plotly_chart(fig6, use_container_width=True, key="partnerships_breakdown_team")
            
            min_30_plus_team = team_stats_middle.loc[team_stats_middle['30+'].idxmin(), 'Team']
            min_30_plus_count = team_stats_middle['30+'].min()
            
            st.info(f"**Key takeaway:** {min_30_plus_team} middle order has the least number of 30+ partnerships ({min_30_plus_count}) in the tournament!")
    
    else:
        st.warning("No partnership data available for the selected filters")
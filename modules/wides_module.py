import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_wides_dashboard(df, selected_teams, selected_matches):
    """
    Render the wides analysis dashboard
    Dedicated module for wides analysis
    """
    
    # =========================
    # SIDEBAR FILTERS
    # =========================
    st.sidebar.markdown("### 🎯 Wides Filters")
    
    # Filter 1: Phase Selector
    phase_options = [
        'Entire Innings',
        'Powerplay (Overs 1–6)',
        'Middle Overs (7–15)',
        'Middle Overs 1 (7–10)',
        'Middle Overs 2 (11–15)',
        'Death Overs (16–20)'
    ]
    selected_phase = st.sidebar.selectbox(
        "🏏 Select Phase:",
        phase_options,
        index=0,
        key="wides_phase_selector"
    )
    
    st.sidebar.markdown("---")
    
    # Filter 2: Bowler Type
    bowler_type_options = ['Both', 'Spinners', 'Seamers']
    selected_bowler_type = st.sidebar.selectbox(
        "⚡ Select Bowler Type:",
        bowler_type_options,
        index=0,
        key="wides_bowler_selector"
    )
    
    st.sidebar.markdown("---")
    
    # Show active filters
    st.sidebar.info(f"""
    **Active Filters:**
    - Phase: {selected_phase}
    - Bowler Type: {selected_bowler_type}
    """)
    
    # =========================
    # HELPER FUNCTIONS
    # =========================
    def get_batting_team(row):
        """Determine which team was batting based on innings"""
        if row['innings'] == 1:
            return row['team1_battingfirst']
        else:
            return row['team2_battingsecond']
    
    def calculate_wides_by_team(data, phase_filter, bowler_type_filter):
        """Calculate runs from wides for each team based on filters"""
        
        # Apply phase filter
        if phase_filter == 'Powerplay (Overs 1–6)':
            df_filtered = data[data['over'] < 6].copy()
        elif phase_filter == 'Middle Overs (7–15)':
            df_filtered = data[(data['over'] >= 6) & (data['over'] < 15)].copy()
        elif phase_filter == 'Middle Overs 1 (7–10)':
            df_filtered = data[(data['over'] >= 6) & (data['over'] < 10)].copy()
        elif phase_filter == 'Middle Overs 2 (11–15)':
            df_filtered = data[(data['over'] >= 10) & (data['over'] < 15)].copy()
        elif phase_filter == 'Death Overs (16–20)':
            df_filtered = data[data['over'] >= 15].copy()
        else:  # Entire Innings
            df_filtered = data.copy()
        
        # Apply bowler type filter
        if bowler_type_filter == 'Spinners':
            df_filtered = df_filtered[df_filtered['pace_or_spin'] == 'spin'].copy()
        elif bowler_type_filter == 'Seamers':
            df_filtered = df_filtered[df_filtered['pace_or_spin'] == 'pace'].copy()
        # 'Both' means no filtering on pace_or_spin
        
        # Filter for wides only
        wides_df = df_filtered[df_filtered['extra_type'] == 'Wide'].copy()
        
        # Add batting team column
        wides_df['batting_team'] = wides_df.apply(get_batting_team, axis=1)
        
        # Calculate total runs from wides per team (extras column contains the wide runs)
        if not wides_df.empty:
            team_wides = wides_df.groupby('batting_team')['extras'].sum().reset_index()
            team_wides.columns = ['Team', 'Runs_from_Wides']
            return team_wides.sort_values('Runs_from_Wides', ascending=False)
        else:
            return pd.DataFrame(columns=['Team', 'Runs_from_Wides'])
    
    def create_team_short_name(team_name):
        """Create abbreviated team names for display"""
        # For APL teams, create shortened versions
        words = team_name.split()
        if len(words) > 2:
            return ' '.join(words[:2]).upper() + '...'
        return team_name.upper()
    
    def plot_wides_chart(team_wides_data):
        """Create a bar chart for runs from wides matching the reference image style"""
        
        if team_wides_data.empty:
            st.warning("No data available for the selected filters.")
            return
        
        # Create short names for teams
        team_wides_data['Short_Name'] = team_wides_data['Team'].apply(create_team_short_name)
        
        # Calculate overall average
        overall_avg = team_wides_data['Runs_from_Wides'].mean()
        
        # Define color palette (matching reference image colors)
        colors = ['#F4D03F', '#58D68D', '#52BE80', '#9B870C', '#45B39D', 
                  '#F8C471', '#76D7C4', '#85C1E2']
        
        # Assign colors to bars
        bar_colors = [colors[i % len(colors)] for i in range(len(team_wides_data))]
        
        # Create the bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=team_wides_data['Short_Name'],
            y=team_wides_data['Runs_from_Wides'],
            text=team_wides_data['Runs_from_Wides'],
            textposition='outside',
            textfont=dict(size=14, color='black', family='Arial Black'),
            marker=dict(
                color=bar_colors,
                line=dict(color='rgba(0,0,0,0.3)', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Runs from Wides: %{y}<extra></extra>'
        ))
        
        # Add average line
        fig.add_hline(
            y=overall_avg, 
            line_dash="dash", 
            line_color="gray", 
            line_width=2,
            annotation_text=f"{overall_avg:.1f}",
            annotation_position="right",
            annotation_font_size=12,
            annotation_font_color="gray"
        )
        
        # Update layout to match reference image
        fig.update_layout(
            title={
                'text': 'Runs from Wides',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333', 'family': 'Arial'}
            },
            xaxis=dict(
                title='',
                tickfont=dict(size=11, color='black'),
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor='lightgray'
            ),
            yaxis=dict(
                title='',
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                showline=False,
                tickfont=dict(size=12)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500,
            margin=dict(l=50, r=50, t=80, b=120),
            showlegend=False,
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True, key="wides_by_team_chart")
        
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Teams", len(team_wides_data))
        with col2:
            st.metric("Average Wides", f"{overall_avg:.1f}")
        with col3:
            st.metric("Highest", f"{team_wides_data['Runs_from_Wides'].max()}")
        with col4:
            st.metric("Lowest", f"{team_wides_data['Runs_from_Wides'].min()}")
    
    # =========================
    # MAIN CONTENT
    # =========================
    
    # Header
    st.markdown('<p style="font-size: 42px; font-weight: bold; color: #667eea; text-align: center; margin-bottom: 10px;">Overall - Wides Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 24px; color: #555; text-align: center; margin-bottom: 30px;">Andhra Premier League 2025</p>', unsafe_allow_html=True)
    
    # Calculate and display results
    team_wides = calculate_wides_by_team(df, selected_phase, selected_bowler_type)
    
    # Main content area
    st.markdown("### 📈 Runs from Wides by Team")
    
    if not team_wides.empty:
        plot_wides_chart(team_wides)
        
        # Show detailed table
        with st.expander("📋 View Detailed Data"):
            st.dataframe(
                team_wides[['Team', 'Runs_from_Wides']].style.background_gradient(
                    subset=['Runs_from_Wides'], 
                    cmap='RdYlGn_r'
                ),
                use_container_width=True
            )
    else:
        st.warning("⚠️ No wide deliveries found for the selected filters. Please adjust your filters.")
    
    st.markdown("---")
    
    # =========================
    # ADDITIONAL WIDES ANALYSIS
    # =========================
    
    # Wides by bowler
    st.subheader("🎯 Top Bowlers Conceding Wides")
    
    # Apply same filters for bowler analysis
    if selected_phase == 'Powerplay (Overs 1–6)':
        wides_filtered = df[df['over'] < 6].copy()
    elif selected_phase == 'Middle Overs (7–15)':
        wides_filtered = df[(df['over'] >= 6) & (df['over'] < 15)].copy()
    elif selected_phase == 'Middle Overs 1 (7–10)':
        wides_filtered = df[(df['over'] >= 6) & (df['over'] < 10)].copy()
    elif selected_phase == 'Middle Overs 2 (11–15)':
        wides_filtered = df[(df['over'] >= 10) & (df['over'] < 15)].copy()
    elif selected_phase == 'Death Overs (16–20)':
        wides_filtered = df[df['over'] >= 15].copy()
    else:
        wides_filtered = df.copy()
    
    if selected_bowler_type == 'Spinners':
        wides_filtered = wides_filtered[wides_filtered['pace_or_spin'] == 'spin'].copy()
    elif selected_bowler_type == 'Seamers':
        wides_filtered = wides_filtered[wides_filtered['pace_or_spin'] == 'pace'].copy()
    
    wides_by_bowler = wides_filtered[wides_filtered['extra_type'] == 'Wide'].groupby('bowler')['extras'].agg(['sum', 'count']).reset_index()
    wides_by_bowler.columns = ['Bowler', 'Total_Runs', 'Wide_Count']
    wides_by_bowler = wides_by_bowler.sort_values('Total_Runs', ascending=False).head(10)
    
    if not wides_by_bowler.empty:
        fig_bowler = go.Figure()
        
        fig_bowler.add_trace(go.Bar(
            x=wides_by_bowler['Bowler'],
            y=wides_by_bowler['Total_Runs'],
            text=wides_by_bowler['Total_Runs'],
            textposition='outside',
            textfont=dict(size=12),
            marker=dict(
                color='#E74C3C',
                line=dict(color='rgba(0,0,0,0.3)', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Runs: %{y}<br>Count: ' + wides_by_bowler['Wide_Count'].astype(str) + '<extra></extra>'
        ))
        
        fig_bowler.update_layout(
            title="Top 10 Bowlers by Runs from Wides",
            xaxis=dict(title='', tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(title='Runs from Wides', showgrid=True, gridcolor='lightgray'),
            plot_bgcolor='white',
            height=400,
            margin=dict(l=50, r=50, t=80, b=120)
        )
        
        st.plotly_chart(fig_bowler, use_container_width=True, key="wides_by_bowler_chart")
        
        # Detailed table
        with st.expander("📋 View Bowler Details"):
            st.dataframe(
                wides_by_bowler.style.background_gradient(
                    subset=['Total_Runs'], 
                    cmap='Reds'
                ),
                use_container_width=True
            )
    else:
        st.info("No bowler data available for wides")
    
    st.markdown("---")
    
    # Wides by over analysis
    st.subheader("📊 Wides Distribution by Over")
    
    wides_by_over = wides_filtered[wides_filtered['extra_type'] == 'Wide'].groupby('over')['extras'].sum().reset_index()
    wides_by_over.columns = ['Over', 'Wides']
    
    if not wides_by_over.empty:
        fig_over = go.Figure()
        
        fig_over.add_trace(go.Scatter(
            x=wides_by_over['Over'] + 1,  # Over numbering starts from 1
            y=wides_by_over['Wides'],
            mode='lines+markers',
            line=dict(color='#3498DB', width=3),
            marker=dict(size=8, color='#2980B9'),
            hovertemplate='Over %{x}: %{y} wides<extra></extra>'
        ))
        
        fig_over.update_layout(
            title="Wides per Over",
            xaxis=dict(title='Over', showgrid=True, gridcolor='lightgray'),
            yaxis=dict(title='Total Wides', showgrid=True, gridcolor='lightgray'),
            plot_bgcolor='white',
            height=400
        )
        
        st.plotly_chart(fig_over, use_container_width=True, key="wides_by_over_chart")
    else:
        st.info("No over-wise data available")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def calculate_comprehensive_metrics(df, team_name):
    """Calculate ultra-detailed metrics for a team"""
    
    # Filter for team
    team_batting = df[
        ((df['team1_battingfirst'] == team_name) & (df['innings'] == 1)) |
        ((df['team2_battingsecond'] == team_name) & (df['innings'] == 2))
    ]
    
    team_bowling = df[
        ((df['team1_battingfirst'] != team_name) & (df['innings'] == 1)) |
        ((df['team2_battingsecond'] != team_name) & (df['innings'] == 2))
    ]
    
    if len(team_batting) == 0:
        return None
    
    # Define phases
    phases = {
        'Powerplay (1-6)': (1, 6),
        'Early Middle (7-10)': (7, 10),
        'Late Middle (11-15)': (11, 15),
        'Death (16-20)': (16, 20)
    }
    
    metrics = {
        'team_name': team_name,
        'total_matches': len(df['match_no'].unique()),
        'phases': {},
        'innings_breakdown': {},
        'player_analysis': {},
        'bowling_types': {},
        'extras_discipline': {}
    }
    
    # === PHASE-WISE ANALYSIS ===
    for phase_name, (start_over, end_over) in phases.items():
        phase_batting = team_batting[(team_batting['over'] >= start_over) & (team_batting['over'] <= end_over)]
        phase_bowling = team_bowling[(team_bowling['over'] >= start_over) & (team_bowling['over'] <= end_over)]
        
        # Detailed batting metrics
        bat_runs = phase_batting['runs_offbat'].sum() + phase_batting['extras'].sum()
        bat_balls = len(phase_batting)
        bat_wickets = phase_batting['is_wicket'].sum()
        bat_boundaries = phase_batting['is_boundary'].sum()
        bat_dots = len(phase_batting[phase_batting['runs_offbat'] == 0])
        bat_sr = (bat_runs / bat_balls * 100) if bat_balls > 0 else 0
        bat_rpo = (bat_runs / (bat_balls / 6)) if bat_balls > 0 else 0
        
        # Boundary breakdown
        fours = len(phase_batting[phase_batting['runs_offbat'] == 4])
        sixes = len(phase_batting[phase_batting['runs_offbat'] == 6])
        boundary_percentage = (bat_boundaries / bat_balls * 100) if bat_balls > 0 else 0
        
        # Bowling metrics
        bowl_runs = phase_bowling['runs_offbat'].sum() + phase_bowling['extras'].sum()
        bowl_balls = len(phase_bowling[phase_bowling['extras'] == 0])
        bowl_wickets = phase_bowling['is_wicket'].sum()
        bowl_economy = (bowl_runs / (bowl_balls / 6)) if bowl_balls > 0 else 0
        bowl_dots = len(phase_bowling[phase_bowling['runs_offbat'] == 0])
        bowl_dot_percentage = (bowl_dots / len(phase_bowling) * 100) if len(phase_bowling) > 0 else 0
        
        metrics['phases'][phase_name] = {
            'batting': {
                'runs': int(bat_runs),
                'balls': int(bat_balls),
                'wickets': int(bat_wickets),
                'boundaries': int(bat_boundaries),
                'fours': int(fours),
                'sixes': int(sixes),
                'dots': int(bat_dots),
                'strike_rate': round(bat_sr, 1),
                'run_rate': round(bat_rpo, 2),
                'boundary_percentage': round(boundary_percentage, 1),
                'dot_ball_percentage': round((bat_dots / bat_balls * 100) if bat_balls > 0 else 0, 1)
            },
            'bowling': {
                'runs_conceded': int(bowl_runs),
                'balls': int(bowl_balls),
                'wickets': int(bowl_wickets),
                'dots': int(bowl_dots),
                'economy': round(bowl_economy, 2),
                'dot_ball_percentage': round(bowl_dot_percentage, 1),
                'wickets_per_match': round(bowl_wickets / metrics['total_matches'], 1)
            }
        }
    
    # === INNINGS BREAKDOWN (1st vs 2nd) ===
    first_inn = team_batting[team_batting['innings'] == 1]
    second_inn = team_batting[team_batting['innings'] == 2]
    
    for inn_type, inn_data in [('1st Innings', first_inn), ('2nd Innings', second_inn)]:
        if len(inn_data) > 0:
            inn_runs = inn_data['runs_offbat'].sum() + inn_data['extras'].sum()
            inn_balls = len(inn_data)
            inn_wickets = inn_data['is_wicket'].sum()
            
            metrics['innings_breakdown'][inn_type] = {
                'matches': len(inn_data['match_no'].unique()),
                'total_runs': int(inn_runs),
                'avg_score': round(inn_runs / len(inn_data['match_no'].unique()), 1) if len(inn_data['match_no'].unique()) > 0 else 0,
                'strike_rate': round((inn_runs / inn_balls * 100) if inn_balls > 0 else 0, 1),
                'wickets_lost': int(inn_wickets),
                'avg_wickets': round(inn_wickets / len(inn_data['match_no'].unique()), 1) if len(inn_data['match_no'].unique()) > 0 else 0
            }
    
    # === PACE VS SPIN (Detailed) ===
    for bowling_type in ['pace', 'spin']:
        vs_type = team_batting[team_batting['pace_or_spin'] == bowling_type]
        
        if len(vs_type) > 0:
            type_runs = vs_type['runs_offbat'].sum()
            type_balls = len(vs_type)
            type_wickets = vs_type['is_wicket'].sum()
            type_boundaries = vs_type['is_boundary'].sum()
            
            # Phase-wise breakdown for pace/spin
            phase_breakdown = {}
            for phase_name, (start, end) in phases.items():
                phase_data = vs_type[(vs_type['over'] >= start) & (vs_type['over'] <= end)]
                if len(phase_data) > 0:
                    p_runs = phase_data['runs_offbat'].sum()
                    p_balls = len(phase_data)
                    phase_breakdown[phase_name] = {
                        'sr': round((p_runs / p_balls * 100) if p_balls > 0 else 0, 1),
                        'runs': int(p_runs),
                        'balls': int(p_balls)
                    }
            
            metrics['bowling_types'][f'vs_{bowling_type}'] = {
                'strike_rate': round((type_runs / type_balls * 100) if type_balls > 0 else 0, 1),
                'runs': int(type_runs),
                'balls': int(type_balls),
                'wickets': int(type_wickets),
                'boundaries': int(type_boundaries),
                'average': round((type_runs / type_wickets) if type_wickets > 0 else type_runs, 1),
                'phase_breakdown': phase_breakdown
            }
    
    # === BOWLING TO LHB/RHB ===
    bowling_to_lhb = team_bowling[team_bowling['batting_hand'] == 'Left']
    bowling_to_rhb = team_bowling[team_bowling['batting_hand'] == 'Right']
    
    for hand_type, hand_data in [('to_LHB', bowling_to_lhb), ('to_RHB', bowling_to_rhb)]:
        if len(hand_data) > 0:
            hand_runs = hand_data['runs_offbat'].sum() + hand_data['extras'].sum()
            hand_balls = len(hand_data[hand_data['extras'] == 0])
            hand_wickets = hand_data['is_wicket'].sum()
            
            metrics['bowling_types'][hand_type] = {
                'economy': round((hand_runs / (hand_balls / 6)) if hand_balls > 0 else 0, 2),
                'wickets': int(hand_wickets),
                'runs': int(hand_runs),
                'balls': int(hand_balls)
            }
    
    # === EXTRAS DISCIPLINE ===
    extras_conceded = team_bowling['extras'].sum()
    wides = len(team_bowling[team_bowling['extra_type'] == 'Wide'])
    noballs = len(team_bowling[team_bowling['extra_type'] == 'NB'])
    
    # Phase-wise extras
    extras_by_phase = {}
    for phase_name, (start, end) in phases.items():
        phase_extras = team_bowling[(team_bowling['over'] >= start) & (team_bowling['over'] <= end)]
        phase_wides = len(phase_extras[phase_extras['extra_type'] == 'Wide'])
        
        extras_by_phase[phase_name] = {
            'wides': int(phase_wides),
            'total_extras': int(phase_extras['extras'].sum())
        }
    
    metrics['extras_discipline'] = {
        'total_extras': int(extras_conceded),
        'wides': int(wides),
        'noballs': int(noballs),
        'extras_per_match': round(extras_conceded / metrics['total_matches'], 1),
        'wides_per_match': round(wides / metrics['total_matches'], 1),
        'by_phase': extras_by_phase
    }
    
    # === POSITION-WISE STATS (Top 3 positions) ===
    position_stats = {}
    for pos in range(1, 4):
        # This is a simplified version - in real implementation, you'd track batting positions
        position_stats[f'Position {pos}'] = {
            'avg_runs': 0,  # Would calculate from actual position data
            'strike_rate': 0
        }
    
    metrics['position_stats'] = position_stats
    
    # === PARTNERSHIPS ===
    # Calculate 30+ partnerships
    partnerships_30_plus = 0  # Would calculate from actual data
    partnerships_50_plus = 0
    
    metrics['partnerships'] = {
        '30_plus': partnerships_30_plus,
        '50_plus': partnerships_50_plus
    }
    
    # === OVERALL SUMMARY ===
    total_runs = team_batting['runs_offbat'].sum() + team_batting['extras'].sum()
    total_balls = len(team_batting)
    total_wickets = team_batting['is_wicket'].sum()
    total_boundaries = team_batting['is_boundary'].sum()
    
    bowl_runs_total = team_bowling['runs_offbat'].sum() + team_bowling['extras'].sum()
    bowl_balls_total = len(team_bowling[team_bowling['extras'] == 0])
    bowl_wickets_total = team_bowling['is_wicket'].sum()
    
    metrics['overall'] = {
        'batting_sr': round((total_runs / total_balls * 100) if total_balls > 0 else 0, 1),
        'avg_score': round(total_runs / metrics['total_matches'], 1),
        'total_runs': int(total_runs),
        'wickets_lost': int(total_wickets),
        'boundaries': int(total_boundaries),
        'bowling_economy': round((bowl_runs_total / (bowl_balls_total / 6)) if bowl_balls_total > 0 else 0, 2),
        'wickets_taken': int(bowl_wickets_total),
        'runs_conceded': int(bowl_runs_total)
    }
    
    return metrics

def generate_detailed_takeaways(metrics):
    """Generate comprehensive takeaways with more detail"""
    
    takeaways = {
        'powerplay_batting': [],
        'early_middle_batting': [],
        'late_middle_batting': [],
        'death_batting': [],
        'powerplay_bowling': [],
        'early_middle_bowling': [],
        'late_middle_bowling': [],
        'death_bowling': [],
        'innings_comparison': [],
        'pace_spin': [],
        'batting_to_lhb_rhb': [],
        'extras': [],
        'overall': []
    }
    
    # Extract phase data
    pp = metrics['phases']['Powerplay (1-6)']
    em = metrics['phases']['Early Middle (7-10)']
    lm = metrics['phases']['Late Middle (11-15)']
    death = metrics['phases']['Death (16-20)']
    
    # === POWERPLAY BATTING ===
    if pp['batting']['strike_rate'] > 140:
        takeaways['powerplay_batting'].append(('GREEN', f"🔥 Explosive powerplay batting! Strike rate of {pp['batting']['strike_rate']} - Among the most aggressive starts in the league"))
    elif pp['batting']['strike_rate'] > 130:
        takeaways['powerplay_batting'].append(('GREEN', f"Excellent powerplay strike rate of {pp['batting']['strike_rate']} - Aggressive intent from ball one"))
    elif pp['batting']['strike_rate'] < 110:
        takeaways['powerplay_batting'].append(('RED', f"⚠️ Slow powerplay starts! SR of {pp['batting']['strike_rate']} puts pressure on middle overs - Need more intent upfront"))
    elif pp['batting']['strike_rate'] < 120:
        takeaways['powerplay_batting'].append(('RED', f"Below par powerplay SR ({pp['batting']['strike_rate']}) - Missing opportunities in field restrictions"))
    
    if pp['batting']['wickets'] == 0:
        takeaways['powerplay_batting'].append(('GREEN', f"💪 Rock solid powerplay - NO wickets lost! Perfect platform for acceleration"))
    elif pp['batting']['wickets'] < 1.5:
        takeaways['powerplay_batting'].append(('GREEN', f"Excellent powerplay stability - Only {pp['batting']['wickets']} wickets lost on average"))
    elif pp['batting']['wickets'] > 2:
        takeaways['powerplay_batting'].append(('RED', f"⚠️ CRITICAL: Losing {pp['batting']['wickets']} powerplay wickets - Top order fragility exposed"))
    
    if pp['batting']['boundary_percentage'] > 20:
        takeaways['powerplay_batting'].append(('GREEN', f"Excellent boundary hitting - {pp['batting']['boundary_percentage']}% balls hit for boundaries ({pp['batting']['fours']} fours, {pp['batting']['sixes']} sixes)"))
    elif pp['batting']['boundary_percentage'] < 12:
        takeaways['powerplay_batting'].append(('RED', f"Boundary drought in powerplay - Only {pp['batting']['boundary_percentage']}% boundary balls. Need more attacking shots"))
    
    if pp['batting']['dot_ball_percentage'] < 35:
        takeaways['powerplay_batting'].append(('GREEN', f"Minimizing dot balls well ({pp['batting']['dot_ball_percentage']}%) - Good ball rotation"))
    elif pp['batting']['dot_ball_percentage'] > 45:
        takeaways['powerplay_batting'].append(('RED', f"Too many dots in powerplay ({pp['batting']['dot_ball_percentage']}%) - Not utilizing field restrictions"))
    
    # === EARLY MIDDLE OVERS (7-10) ===
    if em['batting']['run_rate'] > 8.5:
        takeaways['early_middle_batting'].append(('GREEN', f"Strong acceleration in overs 7-10! Run rate of {em['batting']['run_rate']} - Keeping momentum post powerplay"))
    elif em['batting']['run_rate'] < 6.5:
        takeaways['early_middle_batting'].append(('RED', f"⚠️ Major slowdown in overs 7-10 (RR: {em['batting']['run_rate']}) - Losing momentum after powerplay, vulnerable to spin"))
    
    if em['batting']['wickets'] < 1:
        takeaways['early_middle_batting'].append(('GREEN', "Navigating spin well in middle overs - Minimal wickets lost"))
    elif em['batting']['wickets'] > 2:
        takeaways['early_middle_batting'].append(('RED', f"Collapsing in early middle overs - {em['batting']['wickets']} wickets lost. Middle order not delivering"))
    
    # === LATE MIDDLE OVERS (11-15) ===
    if lm['batting']['run_rate'] > 9.5:
        takeaways['late_middle_batting'].append(('GREEN', f"Brilliant platform building! Run rate of {lm['batting']['run_rate']} in overs 11-15 sets up big totals"))
    elif lm['batting']['run_rate'] < 8.0:
        takeaways['late_middle_batting'].append(('RED', f"Struggle to accelerate in overs 11-15 (RR: {lm['batting']['run_rate']}) - Missing the push needed before death"))
    
    if lm['batting']['wickets'] < 2:
        takeaways['late_middle_batting'].append(('GREEN', f"Good batting depth - Only {lm['batting']['wickets']} wickets in late middle overs"))
    elif lm['batting']['wickets'] > 3:
        takeaways['late_middle_batting'].append(('RED', f"Middle order meltdown! Losing {lm['batting']['wickets']} wickets in overs 11-15"))
    
    # === DEATH OVERS BATTING ===
    if death['batting']['strike_rate'] > 160:
        takeaways['death_batting'].append(('GREEN', f"💥 EXPLOSIVE death overs! SR of {death['batting']['strike_rate']} - Elite finishing ability"))
    elif death['batting']['strike_rate'] > 150:
        takeaways['death_batting'].append(('GREEN', f"Strong death overs batting (SR: {death['batting']['strike_rate']}) - Finishing matches well"))
    elif death['batting']['strike_rate'] < 120:
        takeaways['death_batting'].append(('RED', f"⚠️ MAJOR CONCERN: Death overs SR of {death['batting']['strike_rate']} - Can't accelerate when needed most"))
    elif death['batting']['strike_rate'] < 140:
        takeaways['death_batting'].append(('RED', f"Death overs struggles (SR: {death['batting']['strike_rate']}) - Need specialist finishers"))
    
    if death['batting']['sixes'] > 8:
        takeaways['death_batting'].append(('GREEN', f"Power-hitting prowess! {death['batting']['sixes']} sixes in death overs - Clearing boundaries at will"))
    elif death['batting']['sixes'] < 3:
        takeaways['death_batting'].append(('RED', f"Lack of power in death - Only {death['batting']['sixes']} sixes. Need big hitters"))
    
    # === POWERPLAY BOWLING ===
    if pp['bowling']['economy'] < 6.5:
        takeaways['powerplay_bowling'].append(('GREEN', f"🎯 OUTSTANDING powerplay bowling! Economy of {pp['bowling']['economy']} - Choking opposition early"))
    elif pp['bowling']['economy'] < 7.5:
        takeaways['powerplay_bowling'].append(('GREEN', f"Excellent powerplay restriction (Econ: {pp['bowling']['economy']}) - Setting defensive tone"))
    elif pp['bowling']['economy'] > 9.0:
        takeaways['powerplay_bowling'].append(('RED', f"⚠️ Leaking runs in powerplay! Econ of {pp['bowling']['economy']} - Opposition getting easy starts"))
    elif pp['bowling']['economy'] > 8.0:
        takeaways['powerplay_bowling'].append(('RED', f"Expensive powerplay (Econ: {pp['bowling']['economy']}) - Giving away too many early runs"))
    
    if pp['bowling']['wickets'] > 2.5:
        takeaways['powerplay_bowling'].append(('GREEN', f"Strike force! Taking {pp['bowling']['wickets_per_match']:.1f} powerplay wickets per match - Early breakthroughs"))
    elif pp['bowling']['wickets'] < 1:
        takeaways['powerplay_bowling'].append(('RED', f"Not taking early wickets ({pp['bowling']['wickets_per_match']:.1f} per match) - Allowing partnerships to build"))
    
    if pp['bowling']['dot_ball_percentage'] > 45:
        takeaways['powerplay_bowling'].append(('GREEN', f"Excellent dot ball percentage ({pp['bowling']['dot_ball_percentage']}%) in powerplay - Building pressure"))
    elif pp['bowling']['dot_ball_percentage'] < 35:
        takeaways['powerplay_bowling'].append(('RED', f"Not enough dots in powerplay ({pp['bowling']['dot_ball_percentage']}%) - Batters rotating easily"))
    
    # === EARLY MIDDLE BOWLING (7-10) ===
    if em['bowling']['economy'] < 6.5:
        takeaways['early_middle_bowling'].append(('GREEN', f"Spin choke working! Economy of {em['bowling']['economy']} in overs 7-10 - Strangling run flow"))
    elif em['bowling']['economy'] > 9.0:
        takeaways['early_middle_bowling'].append(('RED', f"Spinners being attacked (Econ: {em['bowling']['economy']}) - Losing control in middle phase"))
    
    # === LATE MIDDLE BOWLING (11-15) ===
    if lm['bowling']['economy'] < 8.0:
        takeaways['late_middle_bowling'].append(('GREEN', f"Tight bowling in overs 11-15 (Econ: {lm['bowling']['economy']}) - Restricting acceleration"))
    elif lm['bowling']['economy'] > 10.0:
        takeaways['late_middle_bowling'].append(('RED', f"Bleeding runs in late middle (Econ: {lm['bowling']['economy']}) - Can't contain batters"))
    
    # === DEATH BOWLING ===
    if death['bowling']['economy'] < 9.0:
        takeaways['death_bowling'].append(('GREEN', f"🛡️ ELITE death bowling! Economy of {death['bowling']['economy']} - Defending totals brilliantly"))
    elif death['bowling']['economy'] < 10.5:
        takeaways['death_bowling'].append(('GREEN', f"Good death bowling (Econ: {death['bowling']['economy']}) - Holding nerve under pressure"))
    elif death['bowling']['economy'] > 13.0:
        takeaways['death_bowling'].append(('RED', f"⚠️ DEATH BOWLING CRISIS! Economy of {death['bowling']['economy']} - Matches being lost here"))
    elif death['bowling']['economy'] > 11.5:
        takeaways['death_bowling'].append(('RED', f"Death bowling major concern (Econ: {death['bowling']['economy']}) - Need specialist death bowlers"))
    
    if death['bowling']['wickets_per_match'] > 2:
        takeaways['death_bowling'].append(('GREEN', f"Taking crucial late wickets ({death['bowling']['wickets_per_match']:.1f} per match) - Breaking partnerships"))
    elif death['bowling']['wickets_per_match'] < 1:
        takeaways['death_bowling'].append(('RED', f"Not taking death wickets ({death['bowling']['wickets_per_match']:.1f} per match) - Batters finishing easily"))
    
    # === INNINGS COMPARISON ===
    if '1st Innings' in metrics['innings_breakdown'] and '2nd Innings' in metrics['innings_breakdown']:
        first = metrics['innings_breakdown']['1st Innings']
        second = metrics['innings_breakdown']['2nd Innings']
        
        if first['avg_score'] > second['avg_score'] + 10:
            takeaways['innings_comparison'].append(('GREEN', f"Better at setting targets! Avg score batting first: {first['avg_score']} vs chasing: {second['avg_score']}"))
        elif second['avg_score'] > first['avg_score'] + 10:
            takeaways['innings_comparison'].append(('GREEN', f"Strong chasers! Better when batting 2nd (Avg: {second['avg_score']} vs {first['avg_score']})"))
        
        if first['strike_rate'] > second['strike_rate'] + 5:
            takeaways['innings_comparison'].append(('RED', f"Passive when chasing - SR drops from {first['strike_rate']} to {second['strike_rate']}"))
    
    # === PACE VS SPIN ===
    if 'vs_pace' in metrics['bowling_types'] and 'vs_spin' in metrics['bowling_types']:
        pace_sr = metrics['bowling_types']['vs_pace']['strike_rate']
        spin_sr = metrics['bowling_types']['vs_spin']['strike_rate']
        
        if pace_sr > 130:
            takeaways['pace_spin'].append(('GREEN', f"Dominating pace bowling! Strike rate of {pace_sr} vs pace"))
        elif pace_sr < 100:
            takeaways['pace_spin'].append(('RED', f"⚠️ Pace vulnerability exposed! SR of {pace_sr} vs pace - Getting tied down by fast bowlers"))
        
        if spin_sr > 130:
            takeaways['pace_spin'].append(('GREEN', f"Playing spin superbly (SR: {spin_sr}) - Sweeping and rotating well"))
        elif spin_sr < 100:
            takeaways['pace_spin'].append(('RED', f"⚠️ Spin weakness! SR of {spin_sr} vs spin - Struggling to rotate strike"))
        
        if pace_sr > spin_sr + 20:
            takeaways['pace_spin'].append(('GREEN', f"Clear preference vs pace - {pace_sr - spin_sr:.0f} points higher SR"))
        elif spin_sr > pace_sr + 20:
            takeaways['pace_spin'].append(('GREEN', f"Spin specialists! Playing spin {spin_sr - pace_sr:.0f} points better than pace"))
    
    # === BOWLING TO LHB/RHB ===
    if 'to_LHB' in metrics['bowling_types'] and 'to_RHB' in metrics['bowling_types']:
        to_lhb = metrics['bowling_types']['to_LHB']['economy']
        to_rhb = metrics['bowling_types']['to_RHB']['economy']
        
        if to_rhb < 8.0:
            takeaways['batting_to_lhb_rhb'].append(('GREEN', f"Excellent vs RHB (Econ: {to_rhb}) - Have RHB's number"))
        elif to_rhb > 10.0:
            takeaways['batting_to_lhb_rhb'].append(('RED', f"Struggling vs RHB (Econ: {to_rhb}) - RHB batsmen dominating"))
        
        if to_lhb < 8.0:
            takeaways['batting_to_lhb_rhb'].append(('GREEN', f"Tight vs LHB (Econ: {to_lhb}) - Angles working well"))
        elif to_lhb > 10.0:
            takeaways['batting_to_lhb_rhb'].append(('RED', f"Leaking runs to LHB (Econ: {to_lhb}) - Need different plans"))
    
    # === EXTRAS DISCIPLINE ===
    extras = metrics['extras_discipline']
    
    if extras['extras_per_match'] < 12:
        takeaways['extras'].append(('GREEN', f"Excellent bowling discipline! Only {extras['extras_per_match']:.1f} extras per match"))
    elif extras['extras_per_match'] > 20:
        takeaways['extras'].append(('RED', f"⚠️ Poor discipline! Conceding {extras['extras_per_match']:.1f} extras per match - Giving away free runs"))
    
    if extras['wides_per_match'] < 5:
        takeaways['extras'].append(('GREEN', f"Good line and length - Only {extras['wides_per_match']:.1f} wides per match"))
    elif extras['wides_per_match'] > 10:
        takeaways['extras'].append(('RED', f"Way too many wides ({extras['wides_per_match']:.1f} per match) - Losing accuracy under pressure"))
    
    # Check death overs wides
    death_wides = extras['by_phase']['Death (16-20)']['wides']
    if death_wides > extras['wides'] * 0.4:  # More than 40% in death
        takeaways['extras'].append(('RED', f"Death bowling discipline issue - {death_wides} wides in death overs alone"))
    
    # === OVERALL ===
    overall = metrics['overall']
    
    if overall['avg_score'] > 170:
        takeaways['overall'].append(('GREEN', f"💪 Formidable batting lineup! Average score of {overall['avg_score']} - Among league's best"))
    elif overall['avg_score'] > 160:
        takeaways['overall'].append(('GREEN', f"Strong batting unit - Averaging {overall['avg_score']} runs"))
    elif overall['avg_score'] < 140:
        takeaways['overall'].append(('RED', f"⚠️ Below par totals! Average of {overall['avg_score']} - Need more firepower throughout"))
    
    if overall['bowling_economy'] < 8.0:
        takeaways['overall'].append(('GREEN', f"Elite bowling attack! Overall economy of {overall['bowling_economy']} - Choking opponents"))
    elif overall['bowling_economy'] > 9.5:
        takeaways['overall'].append(('RED', f"Expensive bowling unit (Econ: {overall['bowling_economy']}) - Leaking too many runs"))
    
    if overall['wickets_taken'] > overall['wickets_lost']:
        takeaways['overall'].append(('GREEN', f"Positive W/L ratio - Taking {overall['wickets_taken']} wickets while losing {overall['wickets_lost']}"))
    
    return takeaways

def create_takeaway_box(text, color_type):
    """Create styled takeaway box"""
    if color_type == 'GREEN':
        bg_color = '#d4edda'
        border_color = '#28a745'
        icon = '✅'
        text_color = '#155724'
    else:  # RED
        bg_color = '#f8d7da'
        border_color = '#dc3545'
        icon = '⚠️'
        text_color = '#721c24'
    
    return f"""
    <div style="background: {bg_color}; 
                border-left: 4px solid {border_color}; 
                padding: 12px 16px; 
                margin: 8px 0; 
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="color: {text_color}; margin: 0; font-size: 0.95rem; font-weight: 500; line-height: 1.5;">
            {icon} {text}
        </p>
    </div>
    """

def render_report_dashboard(df, selected_teams, selected_matches):
    """Render ultra-comprehensive executive report"""
    
    # Get user role
    user_role = st.session_state.get('role', 'team_user')
    assigned_team = st.session_state.get('assigned_team', 'ALL')
    
    # Header
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 2.8rem; font-weight: 800;'>
                📊 END OF SEASON REPORT
            </h1>
            <p style='color: rgba(255,255,255,0.95); margin-top: 0.8rem; font-size: 1.3rem;'>
                Ultra-Comprehensive Performance Analysis
            </p>
            <p style='color: rgba(255,255,255,0.85); margin-top: 0.5rem; font-size: 1rem;'>
                Phase-wise • Player-level • Strategic Insights
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Team selection
    if user_role == 'admin':
        all_teams = sorted(df['team1_battingfirst'].unique())
        selected_team = st.selectbox(
            "🏏 Select Team for Detailed Report:",
            options=all_teams,
            key="report_team_selector"
        )
    else:
        selected_team = assigned_team
        st.info(f"📋 Viewing detailed report for: **{assigned_team}**")
    
    # Calculate comprehensive metrics
    with st.spinner("🔍 Generating ultra-detailed season analysis... This may take a moment..."):
        metrics = calculate_comprehensive_metrics(df, selected_team)
        
        if metrics is None:
            st.error("No data available for this team")
            return
        
        takeaways = generate_detailed_takeaways(metrics)
    
    # Display report
    tabs = st.tabs([
        "📊 Executive Summary",
        "🏏 Batting Breakdown",
        "🎯 Bowling Breakdown",
        "⚔️ Matchup Analysis",
        "💡 Strategic Insights"
    ])
    
    # TAB 1: EXECUTIVE SUMMARY
    with tabs[0]:
        st.markdown("## 🎯 Season at a Glance")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Matches Played", metrics['total_matches'])
        with col2:
            st.metric("Avg Score", f"{metrics['overall']['avg_score']} runs")
        with col3:
            st.metric("Batting SR", metrics['overall']['batting_sr'])
        with col4:
            st.metric("Bowling Econ", metrics['overall']['bowling_economy'])
        
        st.markdown("---")
        
        # Top Strengths and Concerns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ TOP 5 STRENGTHS")
            strength_count = 0
            for category, items in takeaways.items():
                if strength_count >= 5:
                    break
                for color, text in items:
                    if color == 'GREEN' and strength_count < 5:
                        st.success(f"✓ {text}")
                        strength_count += 1
        
        with col2:
            st.markdown("### ⚠️ TOP 5 CONCERNS")
            warning_count = 0
            for category, items in takeaways.items():
                if warning_count >= 5:
                    break
                for color, text in items:
                    if color == 'RED' and warning_count < 5:
                        st.error(f"⚡ {text}")
                        warning_count += 1
        
        # Innings Comparison
        if '1st Innings' in metrics['innings_breakdown'] and '2nd Innings' in metrics['innings_breakdown']:
            st.markdown("---")
            st.markdown("### 📈 1st Innings vs 2nd Innings Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first = metrics['innings_breakdown']['1st Innings']
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
                        <h4>BATTING 1ST</h4>
                        <h2 style='font-size: 2.5rem; margin: 0.5rem 0;'>{first['avg_score']}</h2>
                        <p>Average Score ({first['matches']} innings)</p>
                        <p>SR: {first['strike_rate']} | Wickets: {first['avg_wickets']:.1f}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                second = metrics['innings_breakdown']['2nd Innings']
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
                        <h4>BATTING 2ND</h4>
                        <h2 style='font-size: 2.5rem; margin: 0.5rem 0;'>{second['avg_score']}</h2>
                        <p>Average Score ({second['matches']} innings)</p>
                        <p>SR: {second['strike_rate']} | Wickets: {second['avg_wickets']:.1f}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Innings takeaways
            if takeaways.get('innings_comparison'):
                st.markdown("**Key Insights:**")
                for color, text in takeaways['innings_comparison']:
                    st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
    
    # TAB 2: BATTING BREAKDOWN
    with tabs[1]:
        st.markdown("## 🏏 DETAILED BATTING ANALYSIS")
        
        phases = ['Powerplay (1-6)', 'Early Middle (7-10)', 'Late Middle (11-15)', 'Death (16-20)']
        phase_keys = ['powerplay_batting', 'early_middle_batting', 'late_middle_batting', 'death_batting']
        
        for i, (phase, key) in enumerate(zip(phases, phase_keys)):
            phase_data = metrics['phases'][phase]['batting']
            
            st.markdown(f"### {phase}")
            
            # Create visual metrics
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Primary metrics
                metric_cols = st.columns(5)
                with metric_cols[0]:
                    st.metric("Run Rate", f"{phase_data['run_rate']}")
                with metric_cols[1]:
                    st.metric("Strike Rate", f"{phase_data['strike_rate']}")
                with metric_cols[2]:
                    st.metric("Wickets", phase_data['wickets'])
                with metric_cols[3]:
                    st.metric("Boundaries", f"{phase_data['boundaries']}")
                with metric_cols[4]:
                    st.metric("Dot %", f"{phase_data['dot_ball_percentage']}%")
                
                # Boundary breakdown
                st.markdown(f"""
                    <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                        <p style='margin: 0; color: #666;'><strong>Boundary Breakdown:</strong> 
                        {phase_data['fours']} Fours | {phase_data['sixes']} Sixes | 
                        {phase_data['boundary_percentage']}% boundary balls</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Key Takeaways
                st.markdown("**🎯 Key Takeaways**")
                if takeaways.get(key):
                    for color, text in takeaways[key]:
                        st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
                else:
                    st.markdown(create_takeaway_box("Performance within acceptable range", "GREEN"), unsafe_allow_html=True)
            
            if i < len(phases) - 1:
                st.markdown("---")
    
    # TAB 3: BOWLING BREAKDOWN
    with tabs[2]:
        st.markdown("## 🎯 DETAILED BOWLING ANALYSIS")
        
        phases = ['Powerplay (1-6)', 'Early Middle (7-10)', 'Late Middle (11-15)', 'Death (16-20)']
        phase_keys = ['powerplay_bowling', 'early_middle_bowling', 'late_middle_bowling', 'death_bowling']
        
        for i, (phase, key) in enumerate(zip(phases, phase_keys)):
            phase_data = metrics['phases'][phase]['bowling']
            
            st.markdown(f"### {phase}")
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Economy", f"{phase_data['economy']}")
                with metric_cols[1]:
                    st.metric("Wickets/Match", f"{phase_data['wickets_per_match']}")
                with metric_cols[2]:
                    st.metric("Dot Balls", phase_data['dots'])
                with metric_cols[3]:
                    st.metric("Dot %", f"{phase_data['dot_ball_percentage']}%")
                
                st.markdown(f"""
                    <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                        <p style='margin: 0; color: #666;'><strong>Total:</strong> 
                        {phase_data['runs_conceded']} runs in {phase_data['balls']} balls | 
                        {phase_data['wickets']} wickets</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**🎯 Key Takeaways**")
                if takeaways.get(key):
                    for color, text in takeaways[key]:
                        st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
                else:
                    st.markdown(create_takeaway_box("Performance within acceptable range", "GREEN"), unsafe_allow_html=True)
            
            if i < len(phases) - 1:
                st.markdown("---")
    
    # TAB 4: MATCHUP ANALYSIS
    with tabs[3]:
        st.markdown("## ⚔️ MATCHUP ANALYSIS")
        
        # Pace vs Spin Batting
        st.markdown("### 🏏 Batting vs Pace & Spin")
        
        if 'vs_pace' in metrics['bowling_types'] and 'vs_spin' in metrics['bowling_types']:
            col1, col2 = st.columns(2)
            
            with col1:
                pace_data = metrics['bowling_types']['vs_pace']
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 2rem; border-radius: 15px; color: white; text-align: center;'>
                        <h3>vs PACE BOWLING</h3>
                        <h1 style='font-size: 3.5rem; margin: 0.5rem 0;'>{pace_data['strike_rate']}</h1>
                        <p style='font-size: 1.1rem;'>Strike Rate</p>
                        <hr style='border-color: rgba(255,255,255,0.3);'>
                        <p>{pace_data['runs']} runs in {pace_data['balls']} balls</p>
                        <p>{pace_data['boundaries']} boundaries | {pace_data['wickets']} wickets</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                spin_data = metrics['bowling_types']['vs_spin']
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 2rem; border-radius: 15px; color: white; text-align: center;'>
                        <h3>vs SPIN BOWLING</h3>
                        <h1 style='font-size: 3.5rem; margin: 0.5rem 0;'>{spin_data['strike_rate']}</h1>
                        <p style='font-size: 1.1rem;'>Strike Rate</p>
                        <hr style='border-color: rgba(255,255,255,0.3);'>
                        <p>{spin_data['runs']} runs in {spin_data['balls']} balls</p>
                        <p>{spin_data['boundaries']} boundaries | {spin_data['wickets']} wickets</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Pace vs Spin takeaways
            if takeaways.get('pace_spin'):
                st.markdown("**Key Insights:**")
                for color, text in takeaways['pace_spin']:
                    st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Bowling to LHB/RHB
        st.markdown("### 🎯 Bowling to Left & Right Handers")
        
        if 'to_LHB' in metrics['bowling_types'] and 'to_RHB' in metrics['bowling_types']:
            col1, col2 = st.columns(2)
            
            with col1:
                lhb_data = metrics['bowling_types']['to_LHB']
                st.markdown(f"""
                    <div style='background: #fff3cd; padding: 1.5rem; border-left: 4px solid #ffc107; border-radius: 8px;'>
                        <h4>Bowling to LEFT-HANDERS</h4>
                        <h2 style='color: #856404; font-size: 2.5rem; margin: 0.5rem 0;'>{lhb_data['economy']}</h2>
                        <p style='color: #856404;'>Economy Rate</p>
                        <p style='color: #666;'>{lhb_data['runs']} runs | {lhb_data['wickets']} wickets</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                rhb_data = metrics['bowling_types']['to_RHB']
                st.markdown(f"""
                    <div style='background: #d1ecf1; padding: 1.5rem; border-left: 4px solid #17a2b8; border-radius: 8px;'>
                        <h4>Bowling to RIGHT-HANDERS</h4>
                        <h2 style='color: #0c5460; font-size: 2.5rem; margin: 0.5rem 0;'>{rhb_data['economy']}</h2>
                        <p style='color: #0c5460;'>Economy Rate</p>
                        <p style='color: #666;'>{rhb_data['runs']} runs | {rhb_data['wickets']} wickets</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # LHB/RHB takeaways
            if takeaways.get('batting_to_lhb_rhb'):
                st.markdown("**Key Insights:**")
                for color, text in takeaways['batting_to_lhb_rhb']:
                    st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Extras Discipline
        st.markdown("### 🎯 Bowling Discipline & Extras")
        
        extras = metrics['extras_discipline']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Extras", extras['total_extras'])
        with col2:
            st.metric("Wides", f"{extras['wides']} ({extras['wides_per_match']:.1f}/match)")
        with col3:
            st.metric("No Balls", extras['noballs'])
        
        # Phase-wise extras
        st.markdown("**Extras by Phase:**")
        phase_extras_data = []
        for phase, data in extras['by_phase'].items():
            phase_extras_data.append(f"{phase}: {data['total_extras']} extras ({data['wides']} wides)")
        
        st.markdown(" | ".join(phase_extras_data))
        
        # Extras takeaways
        if takeaways.get('extras'):
            st.markdown("**Key Insights:**")
            for color, text in takeaways['extras']:
                st.markdown(create_takeaway_box(text, color), unsafe_allow_html=True)
    
    # TAB 5: STRATEGIC INSIGHTS
    with tabs[4]:
        st.markdown("## 💡 STRATEGIC RECOMMENDATIONS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ KEY STRENGTHS TO MAINTAIN")
            strength_count = 0
            for category, items in takeaways.items():
                for color, text in items:
                    if color == 'GREEN':
                        st.success(f"✓ {text}")
                        strength_count += 1
            
            if strength_count == 0:
                st.info("Building strengths - focus on consistency")
        
        with col2:
            st.markdown("### ⚠️ PRIORITY IMPROVEMENT AREAS")
            warning_count = 0
            for category, items in takeaways.items():
                for color, text in items:
                    if color == 'RED':
                        st.error(f"⚡ {text}")
                        warning_count += 1
            
            if warning_count == 0:
                st.success("No major concerns - maintain performance")
    
    # Download PDF
    st.markdown("---")
    st.markdown("### 📥 Download Comprehensive Report")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📄 Download Full PDF Report",
            data=generate_comprehensive_pdf(metrics, takeaways, selected_team),
            file_name=f"{selected_team.replace(' ', '_')}_Comprehensive_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.info("""
    **📌 Report Legend:**  
    🟢 **GREEN** = Strengths, positive trends, and areas of excellence  
    🔴 **RED** = Areas needing immediate attention and strategic focus
    
    This comprehensive report analyzes every phase, matchup, and scenario to provide actionable insights.
    """)

def generate_comprehensive_pdf(metrics, takeaways, team_name):
    """Generate comprehensive PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Title page
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(f"{team_name}", title_style))
    story.append(Paragraph("COMPREHENSIVE END OF SEASON REPORT", styles['Heading2']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Executive Summary
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Matches Played', str(metrics['total_matches'])],
        ['Average Score', f"{metrics['overall']['avg_score']} runs"],
        ['Batting Strike Rate', str(metrics['overall']['batting_sr'])],
        ['Bowling Economy', str(metrics['overall']['bowling_economy'])],
        ['Wickets Taken', str(metrics['overall']['wickets_taken'])],
        ['Extras Conceded', str(metrics['extras_discipline']['total_extras'])],
    ]
    
    table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Key Strengths
    story.append(Paragraph("KEY STRENGTHS", heading_style))
    strength_count = 0
    for category, items in takeaways.items():
        for color, text in items:
            if color == 'GREEN':
                story.append(Paragraph(f"✓ {text}", styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
                strength_count += 1
                if strength_count >= 10:  # Limit to top 10
                    break
        if strength_count >= 10:
            break
    
    story.append(PageBreak())
    
    # Priority Concerns
    story.append(Paragraph("PRIORITY IMPROVEMENT AREAS", heading_style))
    warning_count = 0
    for category, items in takeaways.items():
        for color, text in items:
            if color == 'RED':
                story.append(Paragraph(f"⚠ {text}", styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
                warning_count += 1
                if warning_count >= 10:  # Limit to top 10
                    break
        if warning_count >= 10:
            break
    
    doc.build(story)
    buffer.seek(0)
    return buffer
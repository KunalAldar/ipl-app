import streamlit as st
st.set_page_config(page_title="🏏 📄 Team-wise & Season-wise Analysis", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import numpy as np
from utils import load_data

matches, deliveries = load_data()


# Sidebar filters
st.sidebar.header("Filter by")
seasons = sorted(matches['season'].dropna().unique())
seasons_with_all = ["All"] + seasons
teams = sorted(matches['team1'].dropna().unique())

# Multiselect for seasons with "All"
selected_seasons = st.sidebar.multiselect("Select Season(s)", seasons_with_all, default="All")
selected_team = st.sidebar.selectbox("Select Team", teams)

st.title(f"🏏 📄 {selected_team} Performance Analysis")

# If "All" is selected, use all seasons
if "All" in selected_seasons:
    filtered_matches = matches[
        (matches['team1'] == selected_team) | (matches['team2'] == selected_team)
    ]
else:
    filtered_matches = matches[
        ((matches['team1'] == selected_team) | (matches['team2'] == selected_team)) &
        (matches['season'].isin(selected_seasons))
    ]

total_matches = filtered_matches.shape[0]

# Wins
wins = filtered_matches[filtered_matches['winner'] == selected_team].shape[0]

# No Results
no_results = filtered_matches[filtered_matches['result'] == 'no result'].shape[0]

# Losses = Matches Played - Wins - No Results
losses = total_matches - wins - no_results

# Win Percentage
win_percentage = round((wins / (total_matches - no_results)) * 100, 2) if (total_matches - no_results) > 0 else 0

# Display Metrics
st.markdown("## 🎯 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches Played", total_matches)
col2.metric("Wins", wins)
col3.metric("Losses", losses)
col4.metric("Win %", f"{win_percentage}%")


# Get match IDs for filtered matches
selected_match_ids = filtered_matches['id'].unique()

# Filter deliveries for the selected team and matches
team_deliveries = deliveries[
    (deliveries['match_id'].isin(selected_match_ids)) &
    (deliveries['batting_team'] == selected_team)
]

# 1. Top Run-Scorers
top_scorers = team_deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(5).reset_index()
top_scorers.columns = ['Batsman', 'Runs']

# 2. Average Score Per Match
match_totals = team_deliveries.groupby('match_id')['total_runs'].sum()
average_score = round(match_totals.mean(), 2)

# 3. Boundary Distribution
boundaries = team_deliveries[team_deliveries['batsman_runs'].isin([4, 6])]
boundary_count = boundaries['batsman_runs'].value_counts().to_dict()
fours = boundary_count.get(4, 0)
sixes = boundary_count.get(6, 0)


st.subheader("🏏 Batting Performance")

# Metrics
st.metric("Average Team Score", average_score)
st.metric("Total Fours", fours)
st.metric("Total Sixes", sixes)

# Top Scorers Table
st.markdown("### 🔝 Top Run-Scorers")# Filter bowling data: team is the *bowling* team now
team_bowling = deliveries[
    (deliveries['match_id'].isin(selected_match_ids)) &
    (deliveries['bowling_team'] == selected_team)
]
st.dataframe(top_scorers, use_container_width=True, hide_index=True)


# Total wickets taken by each bowler (using 'dismissed' column)
wickets_df = team_bowling.groupby('bowler')['dismissed'].sum().astype(int)

# Balls bowled (excluding wides and no-balls)
legal_deliveries = team_bowling[(team_bowling['wide_runs'] == 0) & (team_bowling['noball_runs'] == 0)]
balls_bowled = legal_deliveries.groupby('bowler').size()

# Runs conceded by each bowler
runs_conceded = team_bowling.groupby('bowler')['total_runs'].sum()

# Economy Rate = total_runs / (balls / 6)
economy_rate = (runs_conceded / (balls_bowled / 6)).round(2)

# Strike Rate = balls / wickets
strike_rate = (balls_bowled / wickets_df).replace([np.inf, np.nan], 0).round(2)

# Combine into a dataframe
bowling_stats = pd.DataFrame({
    'Economy Rate': economy_rate,
    'Strike Rate': strike_rate,
    'Wickets': wickets_df
}).dropna().sort_values(by='Wickets', ascending=False).head(5).reset_index()


st.subheader("🎯 Bowling Performance")

st.markdown("### 🔝 Top Wicket-Takers")
st.dataframe(bowling_stats, use_container_width=True)


# stadium performance 

# Filter matches for selected team and season(s)
team_matches = matches[
    (matches['id'].isin(selected_match_ids)) &
    ((matches['team1'] == selected_team) | (matches['team2'] == selected_team))
]

# Merge with deliveries
team_deliveries = deliveries[deliveries['match_id'].isin(team_matches['id'])]
merged = team_deliveries.merge(
    team_matches[['id', 'venue', 'city','season', 'team1', 'team2', 'toss_winner', 'toss_decision', 'winner']],
    left_on='match_id',
    right_on='id'
)


# Assign innings played by selected team
merged['team_inning'] = merged.apply(
    lambda x: 1 if x['batting_team'] == selected_team and x['inning'] == 1
    else (2 if x['batting_team'] == selected_team and x['inning'] == 2 else None),
    axis=1
)

team_innings = merged[merged['team_inning'].notnull()]

# Calculate total runs by match, venue, and innings
score_summary = team_innings.groupby(['match_id', 'city', 'team_inning']).agg({
    'total_runs': 'sum',
    'winner': 'first'
}).reset_index()

# Add result column
score_summary['Result'] = score_summary['winner'].apply(lambda x: 'Win' if x == selected_team else 'Loss')

# Now aggregate by venue and innings
venue_perf = score_summary.groupby(['city', 'team_inning', 'Result'])['total_runs'].mean().reset_index()
venue_perf = venue_perf.rename(columns={'total_runs': 'Avg Score'})
venue_perf['team_inning'] = venue_perf['team_inning'].map({1: 'First Innings', 2: 'Second Innings'})


st.subheader("📍Team Performance based on city")

pivot = venue_perf.pivot_table(
    index='city',
    columns=['team_inning', 'Result'],
    values='Avg Score',
    aggfunc='mean'
).fillna('-')

st.dataframe(pivot)

# Section 1: Team Summary Table
st.subheader(f"📋 Match Summary for {selected_team} in {', '.join(map(str, selected_seasons))}")
st.dataframe(filtered_matches[[ 'city', 'venue', 'winner', 'player_of_match']], hide_index=True)


# --- Footer ---
st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #ffffff;  /* Light solid background */
            text-align: center;
            padding: 10px 0;
            font-size: 15px;
            font-weight: 500;
            color: #000000;  /* Darker text for visibility */
            box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
        }
        .footer a {
            color: #e63946;  /* Deep red link color */
            text-decoration: none;
            font-weight: bold;
        }
    </style>

    <div class="footer">
        Copyright © 2025 | Powered by <b>Streamlit</b> ⚡ | Made with ❤️ by 
        <a href="mailto:kunalaldar08@gmail.com" target="_blank">Kunal Aldar</a>
    </div>
""", unsafe_allow_html=True)
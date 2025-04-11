import streamlit as st
st.set_page_config(page_title="🏏 📄 Bowler-wise Analysis", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
from utils import load_data

matches, deliveries = load_data()

st.title("🏏 📄 Bowler-wise Analysis")
st.markdown("Explore IPL Bowler performance from 2008 to 2019")

# Load your datasets (replace with your file paths or preloaded data)
# deliveries = pd.read_csv('deliveries.csv')
# matches = pd.read_csv('matches.csv')

# Merge with match info if not already merged
merged = deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id')


# Select bowler
bowler_list = sorted(merged['bowler'].unique())
selected_bowler = st.selectbox("Select a Bowler", bowler_list)

# Filter data
bowler_data = merged[merged['bowler'] == selected_bowler]

# Metrics Calculation
wicket_kinds = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
wickets = bowler_data[bowler_data['dismissal_kind'].isin(wicket_kinds)]
total_wickets = len(wickets)

total_runs_conceded = bowler_data['total_runs'].sum()
overs = bowler_data.shape[0] // 6
economy = round(total_runs_conceded / overs, 2) if overs > 0 else 0

strike_rate = round(bowler_data.shape[0] / total_wickets, 2) if total_wickets > 0 else 0

hauls = wickets.groupby(['match_id', 'inning']).size()
four_w = (hauls == 4).sum()
five_w = (hauls >= 5).sum()

bowler_matches = (
    deliveries[deliveries['bowler'] == selected_bowler]['match_id']
    .nunique()
)

# Display Metrics
st.markdown(f"### 📊 {selected_bowler} Bowling Analysis")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Matches Played", bowler_matches)
col2.metric("Total Wickets", total_wickets)
col3.metric("Economy Rate", economy)
col4.metric("Strike Rate", strike_rate)
col5.metric("4W/5W Hauls", f"{four_w}/{five_w}")


merged = deliveries.merge(matches[['id', 'venue', 'season']], left_on='match_id', right_on='id', how='left')

bowler_dismissals = merged[
    (merged['bowler'] == selected_bowler) &
    (merged['dismissal_kind'].notnull())
    ]

bowler_dismissals = merged[
    (merged['bowler'] == selected_bowler) &
    (merged['dismissed'] == 1)
    ]

# Now safely count dismissal types (they'll only be present if they occurred)
dismissal_count = (
    bowler_dismissals['dismissal_kind']
    .value_counts()
    .reset_index()
    )
dismissal_count.columns = ['Dismissal Type', 'Count']

st.subheader("Wickets Taken Types")

cols = st.columns(len(dismissal_count))

for i, row in dismissal_count.iterrows():
    with cols[i]:
        st.metric(label=row['Dismissal Type'], value=int(row['Count']))

# Data: Wickets by Season
seasonal_wickets = wickets.groupby('season').size().reset_index(name='Wickets')

# Data: Wickets by Team
team_wickets = wickets.groupby('batting_team').size().sort_values(ascending=False).reset_index(name='Wickets')
team_wickets = team_wickets.head(10)

# Layout: Side-by-side

c1, c2 = st.columns(2)

# Line Chart: Wickets by Season
with c1:
    st.subheader("🎯 Bowler Total wickets against Teams")
    st.dataframe(team_wickets.rename(columns={'batting_team': 'Team'}), use_container_width=True, hide_index=True)
    
# Table: Wickets by Team
with c2:
    st.subheader("🎯 Bowler Total wickets Per Season")
    fig1, ax1 = plt.subplots(figsize=(10,4))
    sns.lineplot(data=seasonal_wickets, x='season', y='Wickets', marker='o', ax=ax1)
    ax1.set_title("Wickets by Season")
    ax1.set_xlabel("Season")
    ax1.set_ylabel("Wickets")
    
    # Ensure x-axis has integer ticks and shows all seasons
    seasons = sorted(seasonal_wickets['season'].astype(int).unique())
    ax1.set_xticks(seasons)
    ax1.set_xticklabels(seasons, rotation=45)
    
    ax1.grid(False)
    st.pyplot(fig1)


# Make sure venue is there
if 'venue' in merged.columns:

    venue_wickets = bowler_dismissals.groupby('venue').size().reset_index(name='Wickets')
    venue_wickets = venue_wickets.sort_values(by='Wickets', ascending=False).head(10)

    venue_wickets['Venue'] = pd.Categorical(venue_wickets['venue'], categories=venue_wickets['venue'], ordered=True)
    venue_wickets = venue_wickets.set_index('Venue')

    # Boundaries conceded by team
    boundary_deliveries = merged[
        (merged['bowler'] == selected_bowler) &
        (merged['batsman_runs'].isin([4, 6]))
    ]

    boundary_table = boundary_deliveries.groupby(['batting_team', 'batsman_runs']).size().unstack(fill_value=0)
    boundary_table.columns = ['Fours Conceded' if col == 4 else 'Sixes Conceded' for col in boundary_table.columns]
    boundary_table = boundary_table.reset_index()

# Top venues and boundary chart side-by-side
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 4's and 6's Conceded against Team")
    st.dataframe(boundary_table, use_container_width=True)

with col2:
    st.subheader("🎯 Wickets Taken per venue")
    st.dataframe(venue_wickets, use_container_width=True, hide_index=True)
    
# Comparison

st.title("🆚 Compare Bowler")

bowler_list = deliveries['bowler'].unique()
col1, col2 = st.columns(2)

with col1:
    bowler1 = st.selectbox("Select First Bowler", sorted(bowler_list), key='bo1')

with col2:
    bowler2 = st.selectbox("Select Second Bowler", sorted(bowler_list), key='bo2')


def get_bowler_stats(name):
    data = merged[merged['bowler'] == name]
    bowler_matches = deliveries[deliveries['bowler'] == name]['match_id'].nunique()

    total_wickets = data['dismissed'].sum()
    total_runs_conceded = data['total_runs'].sum()
    balls_bowled = len(data)

    economy = round(total_runs_conceded / (balls_bowled / 6), 2) if balls_bowled > 0 else 0
    strike_rate = round(balls_bowled / total_wickets, 2) if total_wickets > 0 else 0

    boundaries = data[data['batsman_runs'].isin([4, 6])]
    boundary_count = boundaries['batsman_runs'].value_counts().to_dict()
    fours_conceded = boundary_count.get(4, 0)
    sixes_conceded = boundary_count.get(6, 0)

    top_venues = (
        data[data['dismissed'] == 1]
        .groupby('venue')
        .size()
        .sort_values(ascending=False)
        .head(5)
        .reset_index(name='Wickets')
    )
    top_venues.columns = ['Venue', 'Wickets']

    return bowler_matches, total_wickets, economy, strike_rate, fours_conceded, sixes_conceded, top_venues

# Get data
b1_matches, b1_wkts, b1_eco, b1_sr, b1_4s, b1_6s, b1_venue = get_bowler_stats(bowler1)
b2_matches, b2_wkts, b2_eco, b2_sr, b2_4s, b2_6s, b2_venue = get_bowler_stats(bowler2)

# Display metrics
m1, m2 = st.columns(2)
with m1:
    st.metric("Matches Played", b1_matches)
    st.metric("Wickets", b1_wkts)
    st.metric("Economy", b1_eco)
    st.metric("Strike Rate", b1_sr)
    st.metric("Fours/Sixes Conceded", f"{b1_4s}/{b1_6s}")
with m2:
    st.metric("Matches Played", b2_matches)
    st.metric("Wickets", b2_wkts)
    st.metric("Economy", b2_eco)
    st.metric("Strike Rate", b2_sr)
    st.metric("Fours/Sixes Conceded", f"{b2_4s}/{b2_6s}")

# Side-by-side Venue Graphs
v1, v2 = st.columns(2)
with v1:
    st.subheader(bowler1)
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=b1_venue, x='Wickets', y='Venue', palette='Purples_d', ax=ax1)
    ax1.set_title("Top Venues")
    ax1.grid(False)
    st.pyplot(fig1)

with v2:
    st.subheader(bowler2)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=b2_venue, x='Wickets', y='Venue', palette='Greens_d', ax=ax2)
    ax2.set_title("Top Venues")
    ax2.grid(False)
    st.pyplot(fig2)

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
import streamlit as st
st.set_page_config(page_title="🏏 📄 Batsman-wise Analysis", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
from utils import load_data

matches, deliveries = load_data()

st.title("🏏 📄 Batsman-wise Analysis")
st.markdown("Explore IPL Batsman performance from 2008 to 2019")

# Function to get batsman runs vs each team
def batsman_run_against_team(name):
    player_data = deliveries[deliveries['batsman'] == name]
    return player_data.groupby('bowling_team')['batsman_runs'].sum().sort_values(ascending=False)

# Select batsman from dropdown
batsman_list = sorted(deliveries['batsman'].unique())
selected_batsman = st.selectbox("Select a Batsman", batsman_list)

# Section: Batsman performance vs teams
st.subheader(f"🎯 {selected_batsman} Batting Analysis")

# Get data for selected batsman
batsman_vs_teams = batsman_run_against_team(selected_batsman).reset_index()
batsman_vs_teams.columns = ['Bowling Team', 'Runs Scored']


batsman_data = deliveries[deliveries['batsman'] == selected_batsman]
total_runs = batsman_data['batsman_runs'].sum()
balls_faced = batsman_data.shape[0]
strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0

batsman_matches = (
    deliveries[deliveries['batsman'] == selected_batsman]['match_id']
    .nunique()
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Matches Played", batsman_matches)

with col2:
    st.metric("Total Runs", total_runs)

with col3:
    st.metric("Balls Faced", balls_faced)

with col4:
    st.metric("Strike Rate", strike_rate)

# -- Batsman dismissal kind --
dismissals = deliveries[
    (deliveries['batsman'] == selected_batsman) & 
    (deliveries['player_dismissed'] == selected_batsman)
]
dismissal_types = dismissals['dismissal_kind'].value_counts().reset_index()
dismissal_types.columns = ['Dismissal Type', 'Count']

# Show as side-by-side metrics
st.subheader("Dismissal Types")

cols = st.columns(len(dismissal_types))

for i, row in dismissal_types.iterrows():
    with cols[i]:
        st.metric(label=row['Dismissal Type'], value=int(row['Count']))


col1, col2 = st.columns(2)
# Optional: Also show as table
with col1:
    st.subheader(f"🎯 {selected_batsman} Vs Teams")
    st.dataframe(batsman_vs_teams, use_container_width=True, hide_index=True)

# -- Batsman runs per season --
merged = deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id')  # if not already done
player_season_data = merged[merged['batsman'] == selected_batsman]
runs_by_season = player_season_data.groupby('season')['batsman_runs'].sum().reset_index()

with col2:
    st.subheader(f"🎯 {selected_batsman} Runs Over Season")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=runs_by_season, x='season', y='batsman_runs', marker='o', ax=ax1)
    ax1.set_title(f"{selected_batsman} - Runs by Season")
    
    seasons = sorted(runs_by_season['season'].astype(int).unique())
    ax1.set_xticks(seasons)
    ax1.set_xticklabels(seasons, rotation=45)
    
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.grid(False)
    st.pyplot(fig1)


# Merge to bring 'venue' from matches into deliveries
merged = deliveries.merge(matches[['id', 'venue']], left_on='match_id', right_on='id')

# Now filter for selected batsman from the merged data
batsman_data = merged[merged['batsman'] == selected_batsman]

# Calculate boundary counts (4s and 6s) against teams
boundaries = batsman_data[batsman_data['batsman_runs'].isin([4, 6])]
boundary_count = boundaries.groupby(['bowling_team', 'batsman_runs']).size().unstack(fill_value=0).reset_index()
boundary_count.columns = ['Team', 'Fours', 'Sixes']

venue_runs = batsman_data.groupby('venue')['batsman_runs'].sum().reset_index()
venue_runs.columns = ['Venue', 'Total Runs']
venue_runs = venue_runs.sort_values(by='Total Runs', ascending=False).head(10)

# Explicitly set categorical order for Venue (to preserve sort in bar chart)
venue_runs['Venue'] = pd.Categorical(venue_runs['Venue'], categories=venue_runs['Venue'], ordered=True)

# Set index and plot
venue_runs = venue_runs.set_index('Venue')

# Display in two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🎯 {selected_batsman} 4's and 6's over Teams")
    st.dataframe(boundary_count, use_container_width=True, hide_index=True)

with col2:
    st.subheader(f"🎯 {selected_batsman} Runs at Particular Stadium")
    st.bar_chart(venue_runs)



# Comparison of batsman
st.title("🆚 Compare Batsmen")

batsman_list = deliveries['batsman'].unique()
col1, col2 = st.columns(2)

with col1:
    batsman1 = st.selectbox("Select First Batsman", sorted(batsman_list), key='b1')

with col2:
    batsman2 = st.selectbox("Select Second Batsman", sorted(batsman_list), key='b2')

def get_batsman_stats(name):
    data = merged[merged['batsman'] == name]
    total_runs = data['batsman_runs'].sum()
    balls_faced = len(data)
    strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0
    batsman_matches = (
        deliveries[deliveries['batsman'] == selected_batsman]['match_id']
        .nunique()
    )

    boundaries = data[data['batsman_runs'].isin([4, 6])]
    boundary_count = boundaries['batsman_runs'].value_counts().to_dict()
    fours = boundary_count.get(4, 0)
    sixes = boundary_count.get(6, 0)

    top_venues = data.groupby('venue')['batsman_runs'].sum().sort_values(ascending=False).head(5).reset_index()
    top_venues.columns = ['Venue', 'Runs']
    
    return batsman_matches, total_runs, balls_faced, strike_rate, fours, sixes, top_venues

# Get data
b1_batsman_matches, b1_total, b1_balls, b1_sr, b1_fours, b1_sixes, b1_venue = get_batsman_stats(batsman1)
b2_batsman_matches, b2_total, b2_balls, b2_sr, b2_fours, b2_sixes, b2_venue = get_batsman_stats(batsman2)

# Display metrics

m1, m2 = st.columns(2)
with m1:
    st.metric("Matches Played", b1_batsman_matches)
    st.metric("Runs Scored", b1_total)
    st.metric("Strike Rate", b1_sr)
    st.metric("Fours/Sixes", f"{b1_fours}/{b1_sixes}")
with m2:
    st.metric("Matches Played", b2_batsman_matches)
    st.metric("Runs Scored", b2_total)
    st.metric("Strike Rate", b2_sr)
    st.metric("Fours/Sixes", f"{b2_fours}/{b2_sixes}")

# Side-by-side Venue Graphs
v1, v2 = st.columns(2)
with v1:
    st.subheader(batsman1)
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=b1_venue, x='Runs', y='Venue', palette='Blues_d', ax=ax1)
    ax1.set_title("Top Venues")
    ax1.grid(False)
    st.pyplot(fig1)

with v2:
    st.subheader(batsman2)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=b2_venue, x='Runs', y='Venue', palette='Oranges_d', ax=ax2)
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





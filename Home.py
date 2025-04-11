import streamlit as st
st.set_page_config(page_title="IPL Dashboard", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils import load_data  # if using a utils.py file

# Load and preprocess data
matches, deliveries = load_data()

st.title("🏏 IPL Data Analysis Dashboard")
st.markdown("Explore overall trends from IPL 2008–2019 including toss patterns, top players, team wins, and more.")


team_list = sorted(matches['team1'].dropna().unique())
col1, col2 = st.columns(2)

with col1:
    team_a = st.selectbox("Select Team A", team_list, key='team_a')
with col2:
    team_b = st.selectbox("Select Team B", [t for t in team_list if t != team_a], key='team_b')

head_to_head = matches[
    ((matches['team1'] == team_a) & (matches['team2'] == team_b)) |
    ((matches['team1'] == team_b) & (matches['team2'] == team_a))
]

wins = head_to_head['winner'].value_counts().to_dict()

team_a_wins = wins.get(team_a, 0)
team_b_wins = wins.get(team_b, 0)
no_result = len(head_to_head) - team_a_wins - team_b_wins

st.subheader(f"🏏 Head-to-Head: {team_a} vs {team_b}")

col1, col2, col3 = st.columns(3)
col1.metric(f"{team_a} Wins", team_a_wins)
col2.metric(f"{team_b} Wins", team_b_wins)
col3.metric("No Result / Tied", no_result)


# First, ensure matches and deliveries are loaded
# merged should be deliveries merged with matches on 'id' and 'match_id'

# Get final matches (Assumes 'final' matches have 'Final' in the 'match_type' or are the last match of each season)
finals = matches.sort_values(by='date').dropna(subset=['season'])
finals = finals.groupby('season').tail(1)  # Assuming last match of each season is the final

summary = []

for season in finals['season'].unique():
    final_match = finals[finals['season'] == season].iloc[0]
    final_id = final_match['id']
    team1 = final_match['team1']
    team2 = final_match['team2']
    winner = final_match['winner']

    # Filter deliveries of the current season
    season_matches = matches[matches['season'] == season]['id'].unique()
    season_deliveries = deliveries[deliveries['match_id'].isin(season_matches)]

    # Orange Cap: top run scorer
    orange = (
        season_deliveries.groupby('batsman')['batsman_runs'].sum()
        .sort_values(ascending=False)
        .reset_index()
        .iloc[0]
    )
    orange_cap = orange['batsman']

    # Purple Cap: top wicket-taker
    season_merged = season_deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    purple = (
        season_merged[season_merged['dismissed'] == 1]
        .groupby('bowler')
        .size()
        .sort_values(ascending=False)
        .reset_index()
        .iloc[0]
    )
    purple_cap = purple['bowler']

    summary.append({
        'Season': season,
        'Finalist 1': team1,
        'Finalist 2': team2,
        'Winner': winner,
        'Orange Cap': orange_cap,
        'Purple Cap': purple_cap
    })

# Create DataFrame and show
summary_df = pd.DataFrame(summary).sort_values(by='Season', ascending=True).reset_index(drop=True)
st.subheader("🏆 Season Summary")
st.dataframe(summary_df, hide_index=True)

# --- Total matches played over the season ---
st.subheader("📊 Total matches played over the season")
fig4, ax4 = plt.subplots(figsize=(8, 4))
sns.countplot(x='season',data=matches,palette=sns.color_palette('winter'), ax=ax4)  
st.pyplot(fig4)

# --- Toss Decision Over Seasons ---
st.subheader("📊 Toss Decision Over the Seasons")
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.countplot(data=matches, x='season', hue='toss_decision', palette='rocket', ax=ax3)
st.pyplot(fig3)

# --- Toss Winners ---

toss_winner = matches['toss_winner'].value_counts()
toss_decision_pct = (matches['toss_decision'].value_counts(normalize=True) * 100).round(2)

col1, col2 = st.columns([1, 1])

# Prepare data
slices = toss_winner.values.tolist()
labels = toss_winner.index.tolist()

with col1:
    st.subheader("🥧 Toss Wins Distribution by Team")
    fig1, ax1 = plt.subplots(figsize=(4, 4))  # ✅ Smaller, square plot
    ax1.pie(
        slices,
        labels=labels,
        shadow=True,
        autopct='%1.1f%%',
        pctdistance=0.85,
        wedgeprops={'edgecolor': 'black'}
    )
    ax1.set_title("Toss Wins by Team", fontsize=14)
    ax1.axis('equal')
    st.pyplot(fig1)

with col2:
    st.subheader("🧠 Toss Decision Preference")
    fig2, ax2 = plt.subplots(figsize=(4, 4))  # Smaller size
    ax2.pie(toss_decision_pct, labels=toss_decision_pct.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)


# --- Max Run Victory ---
st.subheader("🚀 Match Won by Largest Margin (Runs)")
max_run_win = matches.iloc[[matches['win_by_runs'].idxmax()]][['season', 'city', 'team1', 'team2', 'winner', 'win_by_runs', 'player_of_match']]
st.table(max_run_win)


# --- Top Player of the Match Awards ---
st.subheader("🌟 Top 10 Players with Most 'Player of the Match' Awards")
top_players = matches['player_of_match'].value_counts().head(10)

fig4, ax4 = plt.subplots(figsize=(10, 4))
sns.barplot(x=top_players.values, y=top_players.index, palette="viridis", ax=ax4)
ax4.set_xlabel("Awards")
st.pyplot(fig4)

# --- Total matches played at particular stadium ---

# Calculate venue match count
venue_count = matches['venue'].value_counts(ascending=False).reset_index()
venue_count.columns = ['venue', 'count']

# Plot inside styled container

st.subheader("🏟️ Matches Played per Venue")

fig5, ax5 = plt.subplots(figsize=(12, 10))
sns.barplot(x='count', y='venue', data=venue_count, palette='summer', orient='h', ax=ax5)

# Annotate bars with integer counts
for p in ax5.patches:
    ax5.annotate(f'{int(p.get_width())}', 
        (p.get_width(), p.get_y() + p.get_height() / 2), 
        ha='left', va='center', 
        xytext=(5, 0), 
        textcoords='offset points')

ax5.set_xlabel("Match Count")
ax5.set_ylabel("Venue")
ax5.grid(False)  # Remove grid for clean background

st.pyplot(fig5)

# --- Toss Winner = Match Winner ---
st.subheader("🎯 Matches Where Toss Winner Also Won Match")
toss_match_win_pct = matches[matches['toss_winner'] == matches['winner']].shape[0] / matches.shape[0] * 100
st.metric(label="Toss Winner Also Won the Match", value=f"{toss_match_win_pct:.2f}%")

# --- Moss runs Scored and wickets taken in ipl by batsman ---
batsman_runs = deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).reset_index().head(10)
batsman_runs.columns = ['Batsman', 'Total Runs']

most_wickets=deliveries[deliveries['dismissed']==1]

most_wickets=most_wickets.groupby('bowler')['dismissed'].count().sort_values(ascending=False).head(10).reset_index()
most_wickets.columns = ['Bowler', 'Wickets']

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Top 10 Run Scorers")
    st.dataframe(batsman_runs, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🎯 Top 10 Wicket Takers")
    st.dataframe(most_wickets, use_container_width=True, hide_index=True)

# --- Moss Sixes and fours taken in ipl by batsman ---
most_six=deliveries[deliveries['batsman_runs']==6]
most_six=most_six.groupby('batsman')['batsman_runs'].count().sort_values(ascending=False).head(10).reset_index()


most_fours=deliveries[deliveries['batsman_runs']==4]
most_fours=most_fours.groupby('batsman')['batsman_runs'].count().sort_values(ascending=False).head(10).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Top 10 Six Hitters")
    st.dataframe(most_six, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🎯 Top 10 Four Hitters")
    st.dataframe(most_fours, use_container_width=True, hide_index=True)

# --- Death over Analysis ---

# Filter death overs (over >= 14)
death_overs = deliveries[deliveries['over'] >= 14]

# Filter only sixes
sixes = death_overs[death_overs['batsman_runs'] == 6]

# Create pivot table: Sixes by over and team
pt_six = sixes.pivot_table(
    index='over',
    columns='batting_team',
    values='batsman_runs',
    aggfunc='count',
    fill_value=0
)

# Optional: Reset index for better display
pt_six_display = pt_six.reset_index()

# Display in Streamlit

st.subheader("Death Over Analysis (Overs ≥ 14)")

st.subheader("💥 Sixes in Death Overs by Team")
st.dataframe(pt_six_display, use_container_width=True, hide_index=True)


# Filter only sixes
fours = death_overs[death_overs['batsman_runs'] == 4]

# Create pivot table: Fours by over and team
pt_fours = fours.pivot_table(
    index='over',
    columns='batting_team',
    values='batsman_runs',
    aggfunc='count',
    fill_value=0
)

# Reset index for clean display
pt_fours_display = pt_fours.reset_index()

# Display in Streamlit
st.subheader("🏏 Fours in Death Overs by Team")
st.dataframe(pt_fours_display, use_container_width=True, hide_index=True)

# Filter Wickets
wickets = death_overs[death_overs['dismissed']==1]

# Create pivot table: Wickets per over by team
pt_wickets = wickets.pivot_table(
    index='over',
    columns='bowling_team',
    values='dismissed',
    aggfunc='count',
    fill_value=0
)

# Reset index for clean display
pt_wickets_display = pt_wickets.reset_index()

# Display in Streamlit
st.subheader("🎯 Wickets Taken in Death Overs by Team (Over ≥ 14)")
st.dataframe(pt_wickets_display, use_container_width=True, hide_index=True)


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



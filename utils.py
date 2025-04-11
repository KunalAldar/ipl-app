import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    matches = pd.read_csv("data/matches.csv")
    deliveries = pd.read_csv("data/deliveries.csv")

    matches.replace(['Mumbai Indians','Kolkata Knight Riders','Royal Challengers Bangalore','Deccan Chargers','Chennai Super Kings',
                 'Rajasthan Royals','Delhi Daredevils','Gujarat Lions','Kings XI Punjab',
                 'Sunrisers Hyderabad','Rising Pune Supergiants','Kochi Tuskers Kerala','Pune Warriors','Rising Pune Supergiant']
                ,['MI','KKR','RCB','DC','CSK','RR','DD','GL','KXIP','SRH','RPS','KTK','PW','RPS'],inplace=True)

    deliveries.replace(['Mumbai Indians','Kolkata Knight Riders','Royal Challengers Bangalore','Deccan Chargers','Chennai Super Kings',
                    'Rajasthan Royals','Delhi Daredevils','Gujarat Lions','Kings XI Punjab',
                    'Sunrisers Hyderabad','Rising Pune Supergiants','Kochi Tuskers Kerala','Pune Warriors','Rising Pune Supergiant']
                    ,['MI','KKR','RCB','DC','CSK','RR','DD','GL','KXIP','SRH','RPS','KTK','PW','RPS'],inplace=True)
    
    matches.drop(columns=['umpire3'], inplace=True)

    matches.replace('Rising Pune Supergiant','Rising Pune Supergiants', inplace=True)

    deliveries.fillna(0, inplace=True)

    deliveries['dismissed'] = deliveries['player_dismissed'].apply(lambda x: 1 if x != 0 else 0)
    # Add any preprocessing steps here
    return matches, deliveries
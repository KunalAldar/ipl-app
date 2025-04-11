
🏏 IPL Analysis Dashboard
=========================

An interactive data visualization dashboard to explore and analyze Indian Premier League (IPL) statistics using Python, Streamlit, and various data analysis libraries.

🚀 Live Demo: https://ipl-analysis-dashboard.streamlit.app/

🔍 Features
-----------

- **Batsman Analysis**: View runs, strike rates, boundary counts, top venues, and head-to-head comparisons.
- **Bowler Analysis**: Explore economy, strike rate, wickets, 4W/5W hauls, boundary conceded, and venue stats.
- **Team Analysis**: Filter by season and team to view match stats, batting and bowling performances, venue impact, and best/worst opponents.
- **Head-to-Head**: Compare any two IPL teams across seasons.
- **Season Summary**: See final teams, winners, Orange & Purple Cap holders season-wise.

📊 Tech Stack
-------------

- **Frontend & Dashboard**: Streamlit
- **Data Manipulation**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Deployment**: Streamlit Community Cloud

🧠 How It Works
---------------

- Data is loaded and cleaned from IPL match and delivery datasets.
- Users interact with sidebar filters to dynamically update metrics and visualizations.
- Stats include aggregated and match-level insights with dynamic visuals.

📂 Folder Structure
-------------------

```
.
├── pages/
│   ├── Batsman_analysis.py
│   ├── Bowler_analysis.py
│   ├── Team_performance.py
├── .streamlit/
│   └── config.toml
├── Home.py (main dashboard)
├── data/
│   └── matches.csv, deliveries.csv
└── README.md
```

📚 Learnings and Conclusion
----------------------------

Through building this IPL Analysis Dashboard, I deepened my understanding of data preprocessing, transformation, and visualization using Python, Pandas, Matplotlib, 
Seaborn, and Streamlit. I learned how to derive meaningful insights from raw sports data, such as player performance trends, team comparisons, and match-level analytics. 
The project also strengthened my skills in building interactive dashboards, handling real-world data inconsistencies, and optimizing code for performance. Additionally, 
deploying the app via Streamlit Community Cloud helped me understand the fundamentals of web app deployment. Overall, this project enhanced both my data science and 
frontend presentation abilities, and I'm excited to apply these skills to larger and more complex data-driven challenges in the future.

✨ Powered By
------------

Made with ❤️ using Streamlit  
© 2025 · Created by **Kunal Aldar** · [Contact Me](mailto:kunalaldar@example.com)

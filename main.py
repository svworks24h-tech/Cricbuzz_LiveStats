from __future__ import annotations

import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from api_client import CricbuzzAPI, flatten_matches
from db import execute, get_connection, query_df
from sql_queries import QUERY_TITLES, load_queries

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
.metric-card {padding: 1rem; border-radius: 12px; border: 1px solid rgba(128,128,128,.25);}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def table(sql: str) -> pd.DataFrame:
    return query_df(sql)


def kpi(label: str, value: str) -> None:
    st.metric(label, value)


def home() -> None:
    st.title("🏏 Cricbuzz LiveStats")
    st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")
    st.write("A Streamlit cricket analytics platform combining REST API integration, SQL analytics, player statistics and CRUD data management.")
    c1, c2, c3, c4 = st.columns(4)
    kpi("Players", str(table("SELECT COUNT(*) c FROM players").iloc[0,0]))
    kpi("Matches", str(table("SELECT COUNT(*) c FROM matches").iloc[0,0]))
    kpi("Venues", str(table("SELECT COUNT(*) c FROM venues").iloc[0,0]))
    kpi("SQL Queries", "25")
    st.divider()
    st.markdown("### Modules")
    st.markdown("- **Live Matches** — live/recent match feed with API fallback demo data\n- **Top Player Stats** — batting, bowling and performance leaders\n- **SQL Analytics** — all 25 assignment queries\n- **CRUD Operations** — create, read, update and delete player/match records")
    st.markdown("### Technology")
    st.code("Python • Streamlit • SQLite/SQL • REST API • requests • pandas")
    st.info("For real API data, add RAPIDAPI_KEY to .env. The dashboard remains fully functional with the bundled analytical database when no key is configured.")


def live_matches() -> None:
    st.title("🔴 Live Matches")
    api = CricbuzzAPI()
    if api.enabled:
        try:
            payload = api.live_matches()
            rows = flatten_matches(payload)
            if rows:
                st.success(f"Live API connected — {len(rows)} match(es) returned.")
                for row in rows:
                    with st.container(border=True):
                        st.subheader(f"{row['team1']} vs {row['team2']}")
                        st.write(row["description"])
                        st.caption(f"{row['venue']} {('• ' + row['city']) if row['city'] else ''}")
                        st.write(row["status"] or "Live")
                        if row.get("score"):
                            st.json(row["score"])
                return
            st.warning("API responded but no match objects were found; showing database matches.")
        except Exception as exc:
            st.warning(f"Live API unavailable: {exc}. Showing database fallback.")
    else:
        st.info("API key not configured — showing bundled database matches as a demo fallback.")
    df = table("""
        SELECT m.match_date,m.description,m.format,t1.team_name team1,t2.team_name team2,
               v.venue_name,v.city,m.status,tw.team_name winner,m.win_margin,m.win_type
        FROM matches m JOIN teams t1 ON t1.team_id=m.team1_id JOIN teams t2 ON t2.team_id=m.team2_id
        JOIN venues v ON v.venue_id=m.venue_id LEFT JOIN teams tw ON tw.team_id=m.winner_id
        ORDER BY date(m.match_date) DESC LIMIT 12
    """)
    st.dataframe(df, use_container_width=True, hide_index=True)


def top_stats() -> None:
    st.title("📊 Top Player Stats")
    tabs = st.tabs(["Batting", "Bowling", "Performance"])
    with tabs[0]:
        df = table("""
        SELECT p.full_name,SUM(b.runs) total_runs,MAX(b.runs) highest_score,
               ROUND(1.0*SUM(b.runs)/NULLIF(SUM(CASE WHEN b.dismissed=1 THEN 1 ELSE 0 END),0),2) batting_average,
               SUM(CASE WHEN b.runs>=100 THEN 1 ELSE 0 END) centuries,
               ROUND(100.0*SUM(b.runs)/NULLIF(SUM(b.balls),0),2) strike_rate
        FROM players p JOIN batting_performances b ON b.player_id=p.player_id GROUP BY p.player_id,p.full_name
        ORDER BY total_runs DESC LIMIT 15
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("full_name")["total_runs"])
    with tabs[1]:
        df = table("""
        SELECT p.full_name,SUM(bp.wickets) wickets,SUM(bp.runs_conceded) runs_conceded,
               ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.overs),0),2) economy_rate,
               ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.wickets),0),2) bowling_average
        FROM players p JOIN bowling_performances bp ON bp.player_id=p.player_id GROUP BY p.player_id,p.full_name
        ORDER BY wickets DESC LIMIT 15
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("full_name")["wickets"])
    with tabs[2]:
        df = table("""
        SELECT p.full_name,SUM(b.runs) runs,SUM(bp.wickets) wickets,
               COALESCE(SUM(f.catches),0) catches,COALESCE(SUM(f.stumpings),0) stumpings
        FROM players p LEFT JOIN batting_performances b ON b.player_id=p.player_id
        LEFT JOIN bowling_performances bp ON bp.player_id=p.player_id
        LEFT JOIN fielding_performances f ON f.player_id=p.player_id
        GROUP BY p.player_id,p.full_name ORDER BY runs DESC LIMIT 15
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)


def sql_analytics() -> None:
    st.title("🧮 SQL Queries & Analytics")
    queries = load_queries()
    labels = [f"Q{i}: {QUERY_TITLES[i]}" for i in range(1, 26)]
    selected = st.selectbox("Select query", labels)
    qno = int(selected.split(":", 1)[0][1:])
    st.code(queries[qno], language="sql")
    try:
        df = query_df(queries[qno])
        st.success(f"Query executed successfully — {len(df)} row(s).")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            numeric = df.select_dtypes(include="number").columns
            if len(numeric) >= 1 and len(df) <= 50:
                st.bar_chart(df.set_index(df.columns[0])[numeric[0]])
    except Exception as exc:
        st.error(f"Query execution error: {exc}")


def crud() -> None:
    st.title("🛠️ CRUD Operations")
    entity = st.radio("Entity", ["Players", "Matches"], horizontal=True)
    if entity == "Players":
        tabs = st.tabs(["Create", "Read", "Update", "Delete"])
        with tabs[0]:
            with st.form("create_player"):
                name = st.text_input("Full name")
                country = st.text_input("Country", "India")
                role = st.selectbox("Role", ["Batsman","Bowler","All-rounder","Wicket-keeper"])
                bat = st.text_input("Batting style", "Right-hand")
                bowl = st.text_input("Bowling style", "Right-arm medium")
                if st.form_submit_button("Create player"):
                    if not name.strip(): st.error("Name is required.")
                    else:
                        try:
                            execute("INSERT INTO players(full_name,country,role,batting_style,bowling_style) VALUES(?,?,?,?,?)", (name.strip(),country,role,bat,bowl))
                            table.clear(); st.success("Player created."); st.rerun()
                        except sqlite3.IntegrityError as exc: st.error(str(exc))
        with tabs[1]:
            st.dataframe(table("SELECT * FROM players ORDER BY player_id"), use_container_width=True, hide_index=True)
        with tabs[2]:
            players = table("SELECT player_id,full_name FROM players ORDER BY full_name")
            pid = st.selectbox("Player", players.player_id, format_func=lambda x: players.loc[players.player_id==x,"full_name"].iloc[0])
            current = table(f"SELECT * FROM players WHERE player_id={int(pid)}").iloc[0]
            with st.form("update_player"):
                name = st.text_input("Full name", current.full_name)
                country = st.text_input("Country", current.country)
                role = st.selectbox("Role", ["Batsman","Bowler","All-rounder","Wicket-keeper"], index=["Batsman","Bowler","All-rounder","Wicket-keeper"].index(current.role))
                bat = st.text_input("Batting style", current.batting_style or "")
                bowl = st.text_input("Bowling style", current.bowling_style or "")
                if st.form_submit_button("Update player"):
                    execute("UPDATE players SET full_name=?,country=?,role=?,batting_style=?,bowling_style=? WHERE player_id=?", (name,country,role,bat,bowl,int(pid)))
                    table.clear(); st.success("Player updated."); st.rerun()
        with tabs[3]:
            players = table("SELECT player_id,full_name FROM players ORDER BY full_name")
            pid = st.selectbox("Player to delete", players.player_id, format_func=lambda x: players.loc[players.player_id==x,"full_name"].iloc[0], key="del_player")
            st.warning("Delete is blocked when dependent performance rows exist, preserving referential integrity.")
            if st.button("Delete player", type="primary"):
                try:
                    execute("DELETE FROM players WHERE player_id=?", (int(pid),)); table.clear(); st.success("Player deleted."); st.rerun()
                except sqlite3.IntegrityError: st.error("Cannot delete: player has dependent match-performance records.")
    else:
        tabs = st.tabs(["Create", "Read", "Update", "Delete"])
        teams = table("SELECT team_id,team_name FROM teams ORDER BY team_name")
        venues = table("SELECT venue_id,venue_name FROM venues ORDER BY venue_name")
        series = table("SELECT series_id,series_name FROM series ORDER BY series_name")
        with tabs[0]:
            with st.form("create_match"):
                md = st.date_input("Match date", date.today())
                desc = st.text_input("Description", "T20I Match")
                fmt = st.selectbox("Format", ["Test","ODI","T20I"])
                t1 = st.selectbox("Team 1", teams.team_id, format_func=lambda x: teams.loc[teams.team_id==x,"team_name"].iloc[0])
                t2 = st.selectbox("Team 2", teams.team_id, index=1, format_func=lambda x: teams.loc[teams.team_id==x,"team_name"].iloc[0])
                vid = st.selectbox("Venue", venues.venue_id, format_func=lambda x: venues.loc[venues.venue_id==x,"venue_name"].iloc[0])
                sid = st.selectbox("Series", series.series_id, format_func=lambda x: series.loc[series.series_id==x,"series_name"].iloc[0])
                if st.form_submit_button("Create match"):
                    execute("INSERT INTO matches(series_id,match_date,description,format,venue_id,team1_id,team2_id,status) VALUES(?,?,?,?,?,?,?,?)", (int(sid),md.isoformat(),desc,fmt,int(vid),int(t1),int(t2),"scheduled"))
                    table.clear(); st.success("Match created."); st.rerun()
        with tabs[1]:
            st.dataframe(table("""SELECT m.match_id,m.match_date,m.description,m.format,t1.team_name team1,t2.team_name team2,v.venue_name,m.status FROM matches m JOIN teams t1 ON t1.team_id=m.team1_id JOIN teams t2 ON t2.team_id=m.team2_id JOIN venues v ON v.venue_id=m.venue_id ORDER BY date(m.match_date) DESC"""), use_container_width=True, hide_index=True)
        with tabs[2]:
            matches = table("SELECT match_id,description FROM matches ORDER BY match_id DESC LIMIT 100")
            mid = st.selectbox("Match", matches.match_id, format_func=lambda x: f"{x} — {matches.loc[matches.match_id==x,'description'].iloc[0]}")
            status = st.selectbox("Status", ["scheduled","live","completed"])
            if st.button("Update match status"):
                execute("UPDATE matches SET status=? WHERE match_id=?", (status,int(mid))); table.clear(); st.success("Match updated."); st.rerun()
        with tabs[3]:
            matches = table("SELECT match_id,description FROM matches ORDER BY match_id DESC LIMIT 100")
            mid = st.selectbox("Match to delete", matches.match_id, format_func=lambda x: f"{x} — {matches.loc[matches.match_id==x,'description'].iloc[0]}", key="del_match")
            if st.button("Delete match", type="primary"):
                execute("DELETE FROM matches WHERE match_id=?", (int(mid),)); table.clear(); st.success("Match deleted with dependent innings/performance rows."); st.rerun()


def main() -> None:
    st.sidebar.title("🏏 LiveStats")
    page = st.sidebar.radio("Navigation", ["Home", "Live Matches", "Top Player Stats", "SQL Analytics", "CRUD Operations"])
    st.sidebar.divider()
    st.sidebar.caption("Cricbuzz LiveStats")
    if page == "Home": home()
    elif page == "Live Matches": live_matches()
    elif page == "Top Player Stats": top_stats()
    elif page == "SQL Analytics": sql_analytics()
    else: crud()


if __name__ == "__main__":
    main()

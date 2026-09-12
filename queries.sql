-- Cricbuzz LiveStats - 25 SQL Analytics Queries
-- SQLite syntax. The Streamlit app registers STDDEV_POP for Q19/Q23/Q25.

-- Q1
SELECT full_name, role, batting_style, bowling_style FROM players WHERE country = 'India' ORDER BY full_name;

-- Q2
SELECT m.description, t1.team_name AS team1, t2.team_name AS team2, v.venue_name, v.city, m.match_date
FROM matches m JOIN teams t1 ON t1.team_id=m.team1_id JOIN teams t2 ON t2.team_id=m.team2_id
JOIN venues v ON v.venue_id=m.venue_id
WHERE date(m.match_date) >= date('now','-30 day') ORDER BY date(m.match_date) DESC;

-- Q3
WITH stats AS (
 SELECT p.player_id,p.full_name,m.format,SUM(b.runs) total_runs,
        ROUND(1.0*SUM(b.runs)/NULLIF(SUM(CASE WHEN b.dismissed=1 THEN 1 ELSE 0 END),0),2) batting_average,
        SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) AS centuries
 FROM players p JOIN batting_performances b ON b.player_id=p.player_id
 JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
 WHERE m.format='ODI' GROUP BY p.player_id,p.full_name,m.format)
SELECT full_name,total_runs,batting_average,centuries FROM stats ORDER BY total_runs DESC LIMIT 10;

-- Q4
SELECT venue_name,city,country,capacity FROM venues WHERE capacity>50000 ORDER BY capacity DESC;

-- Q5
SELECT t.team_name, COUNT(m.match_id) total_wins FROM teams t LEFT JOIN matches m ON m.winner_id=t.team_id
GROUP BY t.team_id,t.team_name ORDER BY total_wins DESC;

-- Q6
SELECT role, COUNT(*) player_count FROM players GROUP BY role ORDER BY player_count DESC;

-- Q7
SELECT m.format, MAX(b.runs) highest_score FROM batting_performances b JOIN innings i ON i.innings_id=b.innings_id
JOIN matches m ON m.match_id=i.match_id GROUP BY m.format ORDER BY m.format;

-- Q8
SELECT s.series_name,s.host_country,s.match_type,s.start_date,s.planned_matches
FROM series s WHERE strftime('%Y',s.start_date)='2024' ORDER BY s.start_date;

-- Q9
WITH bat AS (SELECT p.player_id,SUM(b.runs) total_runs FROM players p JOIN batting_performances b ON b.player_id=p.player_id
JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id GROUP BY p.player_id),
bowl AS (SELECT p.player_id,SUM(bp.wickets) total_wickets FROM players p JOIN bowling_performances bp ON bp.player_id=p.player_id
JOIN innings i ON i.innings_id=bp.innings_id JOIN matches m ON m.match_id=i.match_id GROUP BY p.player_id)
SELECT p.full_name,bat.total_runs,bowl.total_wickets FROM players p JOIN bat ON bat.player_id=p.player_id JOIN bowl ON bowl.player_id=p.player_id
WHERE p.role='All-rounder' AND bat.total_runs>1000 AND bowl.total_wickets>50 ORDER BY bat.total_runs DESC;

-- Q10
SELECT m.description,t1.team_name team1,t2.team_name team2,tw.team_name winning_team,m.win_margin victory_margin,m.win_type,v.venue_name
FROM matches m JOIN teams t1 ON t1.team_id=m.team1_id JOIN teams t2 ON t2.team_id=m.team2_id
LEFT JOIN teams tw ON tw.team_id=m.winner_id JOIN venues v ON v.venue_id=m.venue_id
WHERE m.status='completed' ORDER BY date(m.match_date) DESC LIMIT 20;

-- Q11
WITH ps AS (
 SELECT p.player_id,p.full_name,m.format,SUM(b.runs) runs,
        SUM(CASE WHEN b.dismissed=1 THEN 1 ELSE 0 END) outs
 FROM players p JOIN batting_performances b ON b.player_id=p.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
 GROUP BY p.player_id,p.full_name,m.format)
SELECT full_name,
 MAX(CASE WHEN format='Test' THEN runs ELSE 0 END) test_runs,
 MAX(CASE WHEN format='ODI' THEN runs ELSE 0 END) odi_runs,
 MAX(CASE WHEN format='T20I' THEN runs ELSE 0 END) t20_runs,
 ROUND(1.0*SUM(runs)/NULLIF(SUM(outs),0),2) overall_batting_average,
 COUNT(DISTINCT format) formats_played
FROM ps GROUP BY player_id,full_name HAVING formats_played>=2 ORDER BY overall_batting_average DESC;

-- Q12
WITH games AS (
    SELECT m.match_id, m.winner_id, t.team_id, t.team_name,
           v.country AS venue_country, t.country AS team_country
    FROM matches m
    JOIN venues v ON v.venue_id = m.venue_id
    JOIN teams t ON t.team_id = m.team1_id
    UNION ALL
    SELECT m.match_id, m.winner_id, t.team_id, t.team_name,
           v.country AS venue_country, t.country AS team_country
    FROM matches m
    JOIN venues v ON v.venue_id = m.venue_id
    JOIN teams t ON t.team_id = m.team2_id
)
SELECT
    team_name,
    CASE WHEN venue_country = team_country THEN 'Home' ELSE 'Away' END AS location_type,
    SUM(CASE WHEN winner_id = team_id THEN 1 ELSE 0 END) AS wins,
    COUNT(*) AS matches_played
FROM games
GROUP BY team_id, team_name, location_type
ORDER BY team_name, location_type;

-- Q13
SELECT p1.full_name player1,p2.full_name player2,pa.partnership_runs,m.match_id,i.innings_no
FROM partnerships pa JOIN players p1 ON p1.player_id=pa.player1_id JOIN players p2 ON p2.player_id=pa.player2_id
JOIN innings i ON i.innings_id=pa.innings_id JOIN matches m ON m.match_id=i.match_id
WHERE pa.player2_position=pa.player1_position+1 AND pa.partnership_runs>=100 ORDER BY pa.partnership_runs DESC;

-- Q14
SELECT p.full_name,v.venue_name,COUNT(DISTINCT m.match_id) matches_played,
 ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.overs),0),2) avg_economy,
 SUM(bp.wickets) total_wickets
FROM bowling_performances bp JOIN players p ON p.player_id=bp.player_id JOIN innings i ON i.innings_id=bp.innings_id
JOIN matches m ON m.match_id=i.match_id JOIN venues v ON v.venue_id=m.venue_id
GROUP BY p.player_id,p.full_name,v.venue_id,v.venue_name
HAVING COUNT(DISTINCT m.match_id)>=3 AND MIN(bp.overs)>=4 ORDER BY avg_economy,total_wickets DESC;

-- Q15
WITH close_matches AS (
 SELECT * FROM matches WHERE (win_type='runs' AND win_margin<50) OR (win_type='wickets' AND win_margin<5))
SELECT p.full_name,ROUND(AVG(b.runs),2) avg_runs,COUNT(DISTINCT cm.match_id) close_matches_played,
 SUM(CASE WHEN cm.winner_id = i.batting_team_id THEN 1 ELSE 0 END) AS team_wins_when_batted
FROM close_matches cm JOIN innings i ON i.match_id=cm.match_id JOIN batting_performances b ON b.innings_id=i.innings_id
JOIN players p ON p.player_id=b.player_id GROUP BY p.player_id,p.full_name ORDER BY avg_runs DESC;

-- Q16
SELECT p.full_name,strftime('%Y',m.match_date) year,COUNT(DISTINCT m.match_id) matches_played,
 ROUND(AVG(b.runs),2) avg_runs_per_match,
 ROUND(100.0*SUM(b.runs)/NULLIF(SUM(b.balls),0),2) avg_strike_rate
FROM batting_performances b JOIN players p ON p.player_id=b.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
WHERE CAST(strftime('%Y',m.match_date) AS INTEGER)>=2020 GROUP BY p.player_id,p.full_name,year HAVING matches_played>=5 ORDER BY year DESC,avg_runs_per_match DESC;

-- Q17
SELECT toss_decision,COUNT(*) total_matches,
 SUM(CASE WHEN winner_id=toss_winner_id THEN 1 ELSE 0 END) toss_wins,
 ROUND(100.0*SUM(CASE WHEN winner_id=toss_winner_id THEN 1 ELSE 0 END)/COUNT(*),2) toss_win_pct
FROM matches WHERE toss_winner_id IS NOT NULL GROUP BY toss_decision;

-- Q18
SELECT p.full_name,m.format,ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.overs),0),2) economy_rate,SUM(bp.wickets) total_wickets,
 COUNT(DISTINCT m.match_id) matches_bowled,ROUND(AVG(bp.overs),2) avg_overs_per_match
FROM bowling_performances bp JOIN players p ON p.player_id=bp.player_id JOIN innings i ON i.innings_id=bp.innings_id JOIN matches m ON m.match_id=i.match_id
WHERE m.format IN ('ODI','T20I') GROUP BY p.player_id,p.full_name,m.format
HAVING matches_bowled>=10 AND avg_overs_per_match>=2 ORDER BY economy_rate,total_wickets DESC;

-- Q19
SELECT p.full_name,ROUND(AVG(b.runs),2) avg_runs,ROUND(STDDEV_POP(b.runs),2) run_stddev,COUNT(*) innings_count
FROM batting_performances b JOIN players p ON p.player_id=b.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
WHERE b.balls>=10 AND date(m.match_date)>=date('2022-01-01') GROUP BY p.player_id,p.full_name ORDER BY run_stddev;

-- Q20
WITH x AS (
 SELECT p.player_id,p.full_name,m.format,COUNT(DISTINCT m.match_id) matches_played,
 ROUND(1.0*SUM(b.runs)/NULLIF(SUM(CASE WHEN b.dismissed=1 THEN 1 ELSE 0 END),0),2) batting_average
 FROM players p JOIN batting_performances b ON b.player_id=p.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
 GROUP BY p.player_id,p.full_name,m.format)
SELECT full_name,
 MAX(CASE WHEN format='Test' THEN matches_played ELSE 0 END) test_matches,
 MAX(CASE WHEN format='ODI' THEN matches_played ELSE 0 END) odi_matches,
 MAX(CASE WHEN format='T20I' THEN matches_played ELSE 0 END) t20_matches,
 MAX(CASE WHEN format='Test' THEN batting_average END) test_average,
 MAX(CASE WHEN format='ODI' THEN batting_average END) odi_average,
 MAX(CASE WHEN format='T20I' THEN batting_average END) t20_average,
 SUM(matches_played) total_matches FROM x GROUP BY player_id,full_name HAVING total_matches>=20;

-- Q21
WITH bat AS (
 SELECT p.player_id,m.format,SUM(b.runs) runs,
 ROUND(1.0*SUM(b.runs)/NULLIF(SUM(CASE WHEN b.dismissed=1 THEN 1 ELSE 0 END),0),2) batting_average,
 ROUND(100.0*SUM(b.runs)/NULLIF(SUM(b.balls),0),2) strike_rate
 FROM players p JOIN batting_performances b ON b.player_id=p.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id GROUP BY p.player_id,m.format),
bowl AS (
 SELECT p.player_id,m.format,SUM(bp.wickets) wickets,
 ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.wickets),0),2) bowling_average,
 ROUND(1.0*SUM(bp.runs_conceded)/NULLIF(SUM(bp.overs),0),2) economy_rate
 FROM players p JOIN bowling_performances bp ON bp.player_id=p.player_id JOIN innings i ON i.innings_id=bp.innings_id JOIN matches m ON m.match_id=i.match_id GROUP BY p.player_id,m.format),
field AS (SELECT p.player_id,m.format,SUM(f.catches) catches,SUM(f.stumpings) stumpings FROM players p JOIN fielding_performances f ON f.player_id=p.player_id JOIN innings i ON i.innings_id=f.innings_id JOIN matches m ON m.match_id=i.match_id GROUP BY p.player_id,m.format)
SELECT p.full_name,bat.format,
 ROUND((bat.runs*.01)+(bat.batting_average*.5)+(bat.strike_rate*.3),2) batting_points,
 ROUND((bowl.wickets*2)+((50-bowl.bowling_average)*.5)+((6-bowl.economy_rate)*2),2) bowling_points,
 ((field.catches*3)+(field.stumpings*5)) fielding_points,
 ROUND((bat.runs*.01)+(bat.batting_average*.5)+(bat.strike_rate*.3)+(bowl.wickets*2)+((50-bowl.bowling_average)*.5)+((6-bowl.economy_rate)*2)+(field.catches*3)+(field.stumpings*5),2) total_score,
 RANK() OVER (PARTITION BY bat.format ORDER BY ((bat.runs*.01)+(bat.batting_average*.5)+(bat.strike_rate*.3)+(bowl.wickets*2)+((50-bowl.bowling_average)*.5)+((6-bowl.economy_rate)*2)+(field.catches*3)+(field.stumpings*5)) DESC) player_rank
FROM bat JOIN bowl ON bowl.player_id=bat.player_id AND bowl.format=bat.format JOIN field ON field.player_id=bat.player_id AND field.format=bat.format JOIN players p ON p.player_id=bat.player_id
ORDER BY bat.format,player_rank;

-- Q22
WITH recent AS (
 SELECT * FROM matches WHERE date(match_date)>=date('now','-3 year')
), pairs AS (
 SELECT CASE WHEN team1_id<team2_id THEN team1_id ELSE team2_id END a,
 CASE WHEN team1_id<team2_id THEN team2_id ELSE team1_id END b, * FROM recent)
SELECT ta.team_name team_a,tb.team_name team_b,COUNT(*) total_matches,
 SUM(CASE WHEN winner_id=pa.a THEN 1 ELSE 0 END) wins_team_a,
 SUM(CASE WHEN winner_id=pa.b THEN 1 ELSE 0 END) wins_team_b,
 ROUND(100.0*SUM(CASE WHEN winner_id=pa.a THEN 1 ELSE 0 END)/COUNT(*),2) win_pct_team_a,
 ROUND(100.0*SUM(CASE WHEN winner_id=pa.b THEN 1 ELSE 0 END)/COUNT(*),2) win_pct_team_b,
 ROUND(AVG(CASE WHEN winner_id=pa.a THEN win_margin END),2) avg_margin_a,
 ROUND(AVG(CASE WHEN winner_id=pa.b THEN win_margin END),2) avg_margin_b
FROM pairs pa JOIN teams ta ON ta.team_id=pa.a JOIN teams tb ON tb.team_id=pa.b GROUP BY pa.a,pa.b HAVING COUNT(*)>=5 ORDER BY total_matches DESC;

-- Q23
WITH recent AS (
 SELECT p.player_id,p.full_name,m.match_date,b.runs,ROUND(100.0*b.runs/NULLIF(b.balls,0),2) strike_rate,
 ROW_NUMBER() OVER(PARTITION BY p.player_id ORDER BY date(m.match_date) DESC) rn
 FROM batting_performances b JOIN players p ON p.player_id=b.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id),
last10 AS (SELECT * FROM recent WHERE rn<=10),
agg AS (SELECT player_id,full_name,
 ROUND(AVG(CASE WHEN rn<=5 THEN runs END),2) avg_last5,ROUND(AVG(runs),2) avg_last10,
 ROUND(AVG(strike_rate),2) recent_strike_rate, SUM(CASE WHEN runs>50 THEN 1 ELSE 0 END) scores_over_50,
 ROUND(STDDEV_POP(runs),2) consistency_stddev FROM last10 GROUP BY player_id,full_name)
SELECT *,CASE WHEN avg_last5>avg_last10*1.15 AND recent_strike_rate>=130 THEN 'Excellent Form'
 WHEN avg_last5>=avg_last10 AND recent_strike_rate>=110 THEN 'Good Form'
 WHEN avg_last5>=avg_last10*.85 THEN 'Average Form' ELSE 'Poor Form' END form_category FROM agg ORDER BY avg_last5 DESC;

-- Q24
SELECT p1.full_name player1,p2.full_name player2,COUNT(*) partnerships,
 ROUND(AVG(pa.partnership_runs),2) avg_partnership_runs,
 SUM(CASE WHEN pa.partnership_runs>50 THEN 1 ELSE 0 END) partnerships_over_50,
 MAX(pa.partnership_runs) highest_partnership,
 ROUND(100.0*SUM(CASE WHEN pa.partnership_runs>50 THEN 1 ELSE 0 END)/COUNT(*),2) success_rate
FROM partnerships pa JOIN players p1 ON p1.player_id=pa.player1_id JOIN players p2 ON p2.player_id=pa.player2_id
WHERE pa.player2_position=pa.player1_position+1 GROUP BY pa.player1_id,pa.player2_id HAVING partnerships>=5 ORDER BY success_rate DESC,avg_partnership_runs DESC;

-- Q25
WITH q AS (
 SELECT p.player_id,p.full_name,
 strftime('%Y',m.match_date)||'-Q'||(((CAST(strftime('%m',m.match_date) AS INTEGER)-1)/3)+1) quarter,
 AVG(b.runs) avg_runs,100.0*SUM(b.runs)/NULLIF(SUM(b.balls),0) avg_strike_rate,COUNT(DISTINCT m.match_id) matches
 FROM batting_performances b JOIN players p ON p.player_id=b.player_id JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
 GROUP BY p.player_id,p.full_name,quarter),
valid AS (SELECT player_id FROM q GROUP BY player_id HAVING COUNT(*)>=6 AND MIN(matches)>=3),
trend AS (
 SELECT q.*,LAG(avg_runs) OVER(PARTITION BY q.player_id ORDER BY q.quarter) prev_runs,
 LAG(avg_strike_rate) OVER(PARTITION BY q.player_id ORDER BY q.quarter) prev_sr
 FROM q JOIN valid v ON v.player_id=q.player_id)
SELECT full_name,quarter,ROUND(avg_runs,2) avg_runs,ROUND(avg_strike_rate,2) avg_strike_rate,matches,
 CASE WHEN prev_runs IS NULL THEN 'Baseline' WHEN avg_runs>prev_runs*1.05 AND avg_strike_rate>prev_sr THEN 'Improving'
 WHEN avg_runs<prev_runs*.95 AND avg_strike_rate<prev_sr THEN 'Declining' ELSE 'Stable' END quarter_trend
FROM trend ORDER BY full_name,quarter;

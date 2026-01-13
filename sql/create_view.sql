CREATE OR REPLACE VIEW v_match_score AS
SELECT
  m.match_id,
  m.tournament_id,
  m.start_time,
  m.status,

  ht.team_id AS home_team_id,
  ht.name AS home_team_name,

  at.team_id AS away_team_id,
  at.name AS away_team_name,

  SUM(
    CASE
      WHEN e.event_type = 'goal' AND e.team_id = m.home_team_id THEN 1
      WHEN e.event_type = 'own_goal' AND e.team_id = m.away_team_id THEN 1
      ELSE 0
    END
  ) AS home_goals,

  SUM(
    CASE
      WHEN e.event_type = 'goal' AND e.team_id = m.away_team_id THEN 1
      WHEN e.event_type = 'own_goal' AND e.team_id = m.home_team_id THEN 1
      ELSE 0
    END
  ) AS away_goals

FROM matches m
JOIN team ht ON ht.team_id = m.home_team_id
JOIN team at ON at.team_id = m.away_team_id
LEFT JOIN match_event e ON e.match_id = m.match_id

GROUP BY
  m.match_id,
  m.tournament_id,
  m.start_time,
  m.status,
  ht.team_id,
  ht.name,
  at.team_id,
  at.name;
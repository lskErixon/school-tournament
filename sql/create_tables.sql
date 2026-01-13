-- =========================
-- tournament
-- =========================
CREATE TABLE tournament (
  tournament_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

-- =========================
-- team
-- =========================
CREATE TABLE team (
  team_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  class_name VARCHAR(20) NOT NULL,
  rating FLOAT NOT NULL,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0
);

-- =========================
-- player
-- =========================
CREATE TABLE player (
  player_id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  birth_date DATE NOT NULL,
  position VARCHAR(3) NOT NULL,
  CONSTRAINT chk_player_position
    CHECK (position IN ('GK','DEF','MID','ATT')),
  CONSTRAINT fk_player_team
    FOREIGN KEY (team_id) REFERENCES team(team_id)
);

-- =========================
-- matches
-- =========================
CREATE TABLE matches (
  match_id INT AUTO_INCREMENT PRIMARY KEY,
  tournament_id INT NOT NULL,
  home_team_id INT NOT NULL,
  away_team_id INT NOT NULL,
  start_time DATETIME NOT NULL,
  status VARCHAR(10) NOT NULL,
  is_overtime TINYINT(1) NOT NULL DEFAULT 0,

  CONSTRAINT chk_match_status
    CHECK (status IN ('scheduled','live','finished','cancelled')),

  CONSTRAINT fk_match_tournament
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id),

  CONSTRAINT fk_match_home
    FOREIGN KEY (home_team_id) REFERENCES team(team_id),

  CONSTRAINT fk_match_away
    FOREIGN KEY (away_team_id) REFERENCES team(team_id),

  CONSTRAINT chk_match_teams
    CHECK (home_team_id <> away_team_id)
);

-- =========================
-- match_event
-- =========================
CREATE TABLE match_event (
  event_id INT AUTO_INCREMENT PRIMARY KEY,
  match_id INT NOT NULL,
  player_id INT NULL,
  team_id INT NOT NULL,
  minute INT NOT NULL,
  event_type VARCHAR(10) NOT NULL,
  xg FLOAT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT chk_event_type
    CHECK (event_type IN ('goal','own_goal','yellow','red')),

  CONSTRAINT fk_event_match
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
    ON DELETE CASCADE,

  CONSTRAINT fk_event_player
    FOREIGN KEY (player_id) REFERENCES player(player_id)
    ON DELETE SET NULL,

  CONSTRAINT fk_event_team
    FOREIGN KEY (team_id) REFERENCES team(team_id)
);

-- =========================
-- referee
-- =========================
CREATE TABLE referee (
  referee_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  level VARCHAR(10) NOT NULL,
  active TINYINT(1) NOT NULL DEFAULT 1,

  CONSTRAINT chk_referee_level
    CHECK (level IN ('student','teacher','external'))
);

-- =========================
-- match_referee (M:N)
-- =========================
CREATE TABLE match_referee (
  match_id INT NOT NULL,
  referee_id INT NOT NULL,
  PRIMARY KEY (match_id, referee_id),

  CONSTRAINT fk_mr_match
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
    ON DELETE CASCADE,

  CONSTRAINT fk_mr_referee
    FOREIGN KEY (referee_id) REFERENCES referee(referee_id)
);
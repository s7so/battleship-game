CREATE TABLE IF NOT EXISTS saved_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_state TEXT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_saved_games_player 
ON saved_games(player_id); 
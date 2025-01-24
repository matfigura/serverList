CREATE TABLE IF NOT EXISTS server (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    description TEXT,
    votes INTEGER NOT NULL DEFAULT 0,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS skin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_url TEXT,
    votes INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    user_ip TEXT NOT NULL,
    voted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES server (id)
);
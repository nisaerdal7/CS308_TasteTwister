CREATE DATABASE tastetwister;

USE tastetwister;

CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password TEXT NOT NULL,
    token VARCHAR(255) NOT NULL,
    permission BOOLEAN NOT NULL
);

ALTER TABLE users ADD COLUMN picture VARCHAR(255) DEFAULT 'default';


CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    track_name TEXT NOT NULL,
    performer TEXT NOT NULL,
    album TEXT NOT NULL,
    rating INTEGER,
    username VARCHAR(255) NOT NULL,
    permission BOOLEAN,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username),
    UNIQUE (track_name(100), performer(100), album(100), username)
);

ALTER TABLE songs MODIFY rating INTEGER NULL;


CREATE TABLE friendships (
    user1 VARCHAR(255) NOT NULL,
    user2 VARCHAR(255) NOT NULL,
    PRIMARY KEY (user1, user2),
    FOREIGN KEY (user1) REFERENCES users(username),
    FOREIGN KEY (user2) REFERENCES users(username),
    CHECK (user1 <> user2)
);

CREATE TABLE friend_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    status ENUM('pending', 'accepted', 'denied') NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES users(username),
    FOREIGN KEY (receiver) REFERENCES users(username),
    CHECK (sender <> receiver)
);

CREATE TABLE blocked_users (
    blocker VARCHAR(255) NOT NULL,
    blocked VARCHAR(255) NOT NULL,
    PRIMARY KEY (blocker, blocked),
    FOREIGN KEY (blocker) REFERENCES users(username),
    FOREIGN KEY (blocked) REFERENCES users(username),
    CHECK (blocker <> blocked)
);


SELECT * FROM tastetwister.songs;

SELECT * FROM tastetwister.users;

SELECT * FROM tastetwister.friendships;

SELECT * FROM tastetwister.friend_requests;

SELECT * FROM tastetwister.blocked_users;

DESCRIBE tastetwister.songs;


SELECT * FROM tastetwister.blocked_users;
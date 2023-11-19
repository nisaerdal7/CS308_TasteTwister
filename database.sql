CREATE DATABASE tastetwister;

USE tastetwister;

CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password TEXT NOT NULL,
    token VARCHAR(255) NOT NULL,
    permission BOOLEAN NOT NULL
);


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



SELECT * FROM tastetwister.songs;

SELECT * FROM tastetwister.users;


DROP TABLE tastetwister.songs;

DROP TABLE tastetwister.friendships;

DROP TABLE tastetwister.friend_requests;

DROP TABLE tastetwister.users;

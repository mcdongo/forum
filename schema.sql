CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    data BYTEA,
    listed BOOLEAN
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    created_at TIMESTAMP,
    admin BOOLEAN,
    image_id INTEGER
);

CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    topic TEXT,
    rules TEXT,
    listed BOOLEAN
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    topic TEXT,
    message TEXT,
    area_id INTEGER REFERENCES areas,
    posted_at TIMESTAMP,
    op_id INTEGER REFERENCES users,
    listed BOOLEAN,
    image_id INTEGER
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    message TEXT,
    thread_id INTEGER REFERENCES threads,
    area_id INTEGER REFERENCES areas,
    user_id INTEGER REFERENCES users,
    posted_at TIMESTAMP,
    listed BOOLEAN,
    image_id INTEGER
);
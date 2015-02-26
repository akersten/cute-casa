DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY autoincrement,
  email TEXT,
  password TEXT
);
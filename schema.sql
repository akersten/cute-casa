-- Columns starting with e_ are category/restricted type integer values whose details can be found in src/enums.py

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY autoincrement,
  username TEXT NOT NULL UNIQUE,
  displayname TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  registration_date INTEGER DEFAULT (DATETIME('now')),
  cellphone TEXT DEFAULT ""
);


DROP TABLE IF EXISTS households;
CREATE TABLE households (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  household_name TEXT,
  e_household_type INTEGER
);


DROP TABLE IF EXISTS household_memberships;
CREATE TABLE household_memberships (
  user INTEGER,
  household INTEGER,
  e_household_relation INTEGER,
  PRIMARY KEY (user, household),
  FOREIGN KEY(user) REFERENCES users(id)
);


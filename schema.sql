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

-- dwelling_type: 1 for apartment, 2 for house.
DROP TABLE IF EXISTS households;
CREATE TABLE households (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  household_name TEXT,
  household_type INTEGER
);

-- relation: 1 for member, 2 for admin
DROP TABLE IF EXISTS household_memberships;
CREATE TABLE household_memberships (
  user INTEGER,
  household INTEGER,
  relation INTEGER,
  PRIMARY KEY (user, household),
  FOREIGN KEY(user) REFERENCES users(id)
)
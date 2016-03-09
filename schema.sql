-- Columns starting with e_ are category/restricted type integer values whose details can be found in src/enums.py
-- Tables with integer primary keys should always have a column named `id` by convention so the database convenience
--     methods can use them.

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY autoincrement,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  registration_date INTEGER DEFAULT (DATETIME('now')),
  e_user_authority INTEGER NOT NULL DEFAULT 1
);


DROP TABLE IF EXISTS households;
CREATE TABLE households (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  household_name TEXT NOT NULL,
  e_household_type INTEGER NOT NULL,
  created_date INTEGER DEFAULT (DATETIME('now'))
);


DROP TABLE IF EXISTS household_memberships;
CREATE TABLE household_memberships (
  user INTEGER NOT NULL,
  household INTEGER NOT NULL,
  e_household_relation INTEGER NOT NULL,
  membership_date INTEGER DEFAULT (DATETIME('now')),
  PRIMARY KEY (user, household),
  FOREIGN KEY(user) REFERENCES users(id),
  FOREIGN KEY(household) REFERENCES households(id)
);


-- Table for log events..
-- id: the event id (primary key).
-- blame: the user who raised or encountered the event..
-- timestamp: when this event was raised.
-- e_log_event_level: the criticality of the event
-- e_log: the type of event (e.g. system, user, admin)
-- message: the event message
--
DROP TABLE IF EXISTS event_log;
CREATE TABLE event_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  blame INTEGER,
  timestamp INTEGER DEFAULT (DATETIME('now')),
  e_log_event_level INTEGER NOT NULL,
  e_log_event_type INTEGER NOT NULL,
  message TEXT NOT NULL,
  FOREIGN KEY(blame) REFERENCES  users(id)
);





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


-- Table for the administrative logs events.
-- id: the event id.
-- blame: the user who raised the log event.
-- timestamp: when this event was raised.
-- e_log_event_level: the criticality of the event
-- message: the event message
--
DROP TABLE IF EXISTS admin_log_events;
CREATE TABLE admin_log_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  blame INTEGER NOT NULL,
  timestamp INTEGER DEFAULT (DATETIME('now')),
  e_log_event_level INTEGER NOT NULL,
  message TEXT NOT NULL,
  FOREIGN KEY(blame) REFERENCES  users(id)
);

-- Table for the system log events.
-- id: the event id.
-- timestamp: when this event was raised.
-- e_log_event_level: the criticality of the event.
-- message: the event message.
DROP TABLE IF EXISTS system_log_events;
CREATE TABLE system_log_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp INTEGER DEFAULT (DATETIME('now')),
  e_log_event_level INTEGER NOT NULL,
  message TEXT NOT NULL
);
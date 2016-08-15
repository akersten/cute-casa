CHECK_USERNAME = "SELECT COUNT(*) FROM users WHERE username=?"
CHECK_LOGIN = "SELECT COUNT(*),id,email FROM users WHERE username=? AND password=? LIMIT 1"

REGISTER = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"

# ######################################################################################################################
# User profile queries
# ######################################################################################################################

USER_UPDATE_EMAIL = "UPDATE users SET email=? WHERE id=?"

# ######################################################################################################################
# Household profile queries
# ######################################################################################################################

HOUSEHOLD_UPDATE_HOUSEHOLDNAME = "UPDATE households SET household_name=? WHERE id=?"
HOUSEHOLD_UPDATE_HOUSEHOLDTYPE = "UPDATE households SET e_household_type=? WHERE id=?"

HOUSEHOLD_CREATE = "INSERT INTO households(household_name, e_household_type) VALUES (?, ?)"
HOUSEHOLD_SEARCH = "SELECT id, household_name, e_household_type FROM households WHERE household_name LIKE ?"


# #
# Household membership queries
# #

HOUSEHOLD_MEMBERSHIP_ADD = "INSERT INTO household_memberships(user, household, e_household_relation) VALUES (?, ?, ?)"
HOUSEHOLD_MEMBERSHIP_UPDATE = "UPDATE household_memberships SET e_household_relation=? WHERE household=? AND user=?"
HOUSEHOLD_MEMBERSHIP_REMOVE = "DELETE FROM household_memberships WHERE household=? AND user=?"

HOUSEHOLD_MEMBERSHIP_GET_FOR_USER = "SELECT * FROM household_memberships WHERE user=?"
HOUSEHOLD_MEMBERSHIP_GET_FOR_HOUSEHOLD = "SELECT * FROM household_memberships WHERE household=?"
HOUSEHOLD_MEMBERSHIP_GET_FOR_USER_AND_HOUSEHOLD = "SELECT * FROM household_memberships WHERE user=? AND household=?"

HOUSEHOLD_GET_USERS = "SELECT users.id as id," \
                      " household_memberships.e_household_relation as e_household_relation," \
                      " household_memberships.membership_date as membership_date" \
                      " FROM users INNER JOIN household_memberships ON users.id=household_memberships.user" \
                      " WHERE household_memberships.household=?"



# ######################################################################################################################
# Logging queries
# ######################################################################################################################

LOG_INSERT = "INSERT INTO event_log (blame, message, e_log_event_level, e_log_event_type) VALUES (?, ?, ?, ?)"
LOG_GET = "SELECT * FROM event_log WHERE e_log_event_type = ? ORDER BY id DESC LIMIT ?, ?"



# ######################################################################################################################
# User queries
# ######################################################################################################################

USER_GET_HOUSEHOLDS_NO_REQUESTS = "SELECT households.id, households.household_name, households.e_household_type," \
                      " household_memberships.e_household_relation" \
                      " FROM households INNER JOIN household_memberships ON households.id=household_memberships.household" \
                      " WHERE household_memberships.user=? AND household_memberships.e_household_relation<>3"
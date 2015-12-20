CHECK_USERNAME = "SELECT COUNT(*) FROM users WHERE username=?"
CHECK_LOGIN = "SELECT COUNT(*),id,email,cellphone,displayname FROM users WHERE username=? AND password=? LIMIT 1"

REGISTER = "INSERT INTO users (username, displayname, password, email) VALUES (?, ?, ?, ?)"

# ######################################################################################################################
# User profile queries
# ######################################################################################################################

USER_UPDATE_DISPLAYNAME = "UPDATE users SET displayname=? WHERE id=?"
USER_UPDATE_EMAIL = "UPDATE users SET email=? WHERE id=?"
USER_UPDATE_CELLPHONE = "UPDATE users SET cellphone=? WHERE id=?"

# ######################################################################################################################
# Household profile queries
# ######################################################################################################################

HOUSEHOLD_UPDATE_HOUSEHOLDNAME = "UPDATE households SET household_name=? WHERE id=?"
HOUSEHOLD_UPDATE_HOUSEHOLDTYPE = "UPDATE households SET e_household_type=? WHERE id=?"

HOUSEHOLD_CREATE = "INSERT INTO households(household_name, e_household_type) VALUES (?, ?)"



# #
# Household membership queries
# #

HOUSEHOLD_MEMBERSHIP_ADD = "INSERT INTO household_memberships(user, household, e_household_relation) VALUES (?, ?, ?)"
HOUSEHOLD_MEMBERSHIP_GET_FOR_USER = "SELECT * FROM household_memberships WHERE user=?"
HOUSEHOLD_MEMBERSHIP_GET_FOR_HOUSEHOLD = "SELECT * FROM household_memberships WHERE household=?"
HOUSEHOLD_MEMBERSHIP_GET_FOR_USER_AND_HOUSEHOLD = "SELECT * FROM household_memberships WHERE user=? AND household=?"

HOUSEHOLD_GET_USERS = "SELECT users.id as id," \
                      " users.displayname as displayname," \
                      " household_memberships.e_household_relation as e_household_relation," \
                      " household_memberships.membership_date as membership_date" \
                      " FROM users INNER JOIN household_memberships ON users.id=household_memberships.user" \
                      " WHERE household_memberships.household=?"


# ######################################################################################################################
# Administrative logging queries
# ######################################################################################################################

ADMIN_LOG_INSERT = "INSERT INTO admin_log_events (blame, message, e_log_event_level) VALUES (?, ?, ?)"
ADMIN_LOG_GET = "SELECT * FROM admin_log_events ORDER BY id DESC LIMIT ?, ?"

# ######################################################################################################################
# System logging queries
# ######################################################################################################################

SYSTEM_LOG_INSERT = "INSERT INTO system_log_events (message, e_log_event_level) VALUES (?, ?)"
SYSTEM_LOG_GET = "SELECT * FROM system_log_events ORDER BY id DESC LIMIT ?, ?"


# ######################################################################################################################
# User queries
# ######################################################################################################################

USER_GET_HOUSEHOLDS = "SELECT households.id, households.household_name, households.e_household_type," \
                      " household_memberships.e_household_relation" \
                      " FROM households INNER JOIN household_memberships ON households.id=household_memberships.household" \
                      " WHERE household_memberships.user=?"
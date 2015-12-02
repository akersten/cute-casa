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

# ######################################################################################################################
# Administrative logging queries
# ######################################################################################################################

ADMIN_LOG_INSERT = "INSERT INTO admin_log_events (blame, message, e_admin_log_event_level) VALUES (?, ?, ?)"
ADMIN_LOG_GET = "SELECT * FROM admin_log_events ORDER BY id DESC LIMIT ?, ?"

# ######################################################################################################################
# User queries
# ######################################################################################################################

USER_GET_HOUSEHOLDS = "SELECT households.id, households.household_name, households.e_household_type," \
                      " household_memberships.e_household_relation" \
                      " FROM households INNER JOIN household_memberships ON households.id=household_memberships.household" \
                      " WHERE household_memberships.user=?"
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


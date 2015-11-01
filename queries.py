CHECK_USERNAME = "SELECT COUNT(*) FROM users WHERE username=?"
CHECK_LOGIN = "SELECT COUNT(*),id,email,cellphone FROM users WHERE username=? AND password=? LIMIT 1"

REGISTER = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"

# ######################################################################################################################
# User Profile functions
# ######################################################################################################################

USER_UPDATE_EMAIL = "UPDATE users SET email=? WHERE id=?"
USER_UPDATE_CELLPHONE = "UPDATE users SET cellphone=? WHERE id=?"
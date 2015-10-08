CHECK_USERNAME = "SELECT COUNT(*) FROM users WHERE username=?"
CHECK_LOGIN = "SELECT COUNT(*) FROM users WHERE username=? AND password=?"

REGISTER = "INSERT INTO users (username, password) VALUES (?, ?)"
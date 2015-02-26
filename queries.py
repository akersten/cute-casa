CHECK_EMAIL = "SELECT COUNT(*) FROM users WHERE email=?"
CHECK_LOGIN = "SELECT COUNT(*) FROM users WHERE email=? AND password=?"

REGISTER = "INSERT INTO users (email, password) VALUES (?, ?)"
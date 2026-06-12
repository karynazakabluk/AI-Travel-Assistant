import sqlite3

connection = sqlite3.connect("travel.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    destination TEXT NOT NULL,
    region TEXT NOT NULL,
    price INTEGER NOT NULL,
    days INTEGER NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES 
('admin', 'admin123', 'admin'),
('user', 'user123', 'user')
""")

connection.commit()
connection.close()

print("Database and users created successfully")
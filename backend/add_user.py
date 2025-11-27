# add_user.py
import mysql.connector
from werkzeug.security import generate_password_hash

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sanjana@0806",
    "database": "student_portal"
}

def add_user(username, password):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
    conn.commit()
    conn.close()
    print(f"User {username} added successfully!")

# Example usage
add_user("ST001", "password123")
add_user("ST002", "mypassword")
add_user("admin", "admin123")
add_user("arun", "arun@123")
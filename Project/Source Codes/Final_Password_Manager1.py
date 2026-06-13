import sqlite3
import bcrypt
from cryptography.fernet import Fernet

# Function to generate and save the encryption key
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Function to load the encryption key
def load_key():
    return open("secret.key", "rb").read()

# Generate the key if it does not exist
try:
    key = load_key()
except FileNotFoundError:
    generate_key()
    key = load_key()

cipher_suite = Fernet(key)

# Database setup for password manager
conn = sqlite3.connect('password_manager.db')
c = conn.cursor()

# Database setup for account management
account_conn = sqlite3.connect('Account.db')
account_c = account_conn.cursor()

# Create tables if they do not exist
c.execute('''
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY,
    site TEXT,
    username TEXT,
    email TEXT,
    password TEXT,
    category TEXT,
    tags TEXT,
    last_updated TEXT
)
''')
conn.commit()

account_c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT
)
''')
account_conn.commit()

# Function to encrypt data
def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

# Function to decrypt data
def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()

# Function to save a password
# Function to save a password
def save_password(site, username, password):
    if not site or not username or not password:
        raise ValueError("Site, Username, and Password must be provided")
    encrypted_password = encrypt_data(password)
    c.execute("INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)",
              (site, username, encrypted_password))
    conn.commit()

# Function to get all passwords
def get_passwords():
    c.execute("SELECT * FROM passwords")
    passwords = c.fetchall()
    return passwords

# Function to delete a password
def delete_password(password_id):
    c.execute("DELETE FROM passwords WHERE id=?", (password_id,))
    conn.commit()

# Function to create a new account
def create_account(username, email, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    account_c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed_password))
    account_conn.commit()

# Function to authenticate a user
def authenticate(username, password):
    account_c.execute("SELECT password FROM users WHERE username=?", (username,))
    stored_password = account_c.fetchone()
    if stored_password and bcrypt.checkpw(password.encode(), stored_password[0]):
        return True
    return False

# Close the database connections when the script ends
def close_connections():
    conn.close()
    account_conn.close()

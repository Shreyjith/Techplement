import bcrypt
import sqlite3
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import random
import string
import secrets

# Encryption key management
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

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
    website TEXT,
    username TEXT,
    password TEXT
)
''')
conn.commit()

account_c.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    email TEXT,
    hashed_password TEXT,
    last_reset TIMESTAMP
)
''')
account_conn.commit()

# Core functions for password manager
def save_password(website, username, password):
    encrypted_password = cipher_suite.encrypt(password.encode()).decode()
    c.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)", (website, username, encrypted_password))
    conn.commit()

def get_passwords():
    c.execute("SELECT * FROM passwords")
    return c.fetchall()

def delete_password(password_id):
    c.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
    conn.commit()

# Core functions for account management
def create_account(email, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    account_c.execute("INSERT INTO accounts (email, hashed_password) VALUES (?, ?)", (email, hashed_password))
    account_conn.commit()

def authenticate(email, password):
    account_c.execute("SELECT hashed_password FROM accounts WHERE email = ?", (email,))
    record = account_c.fetchone()
    if record and bcrypt.checkpw(password.encode(), record[0].encode()):
        return True
    return False

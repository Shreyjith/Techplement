import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from cryptography.fernet import Fernet
import bcrypt

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the secret key file
key_file_path = 'C:\\Users\\shrey\\OneDrive\\Desktop\\Amrita\\Internship\\Project\\password_manager\\secret.key'

# Load encryption key
def load_key():
    return open(key_file_path, "rb").read()

key = load_key()
cipher_suite = Fernet(key)

# Connect to the account database
account_conn = sqlite3.connect('Account.db', check_same_thread=False)
account_c = account_conn.cursor()

# Connect to the password database
conn = sqlite3.connect('password_manager.db', check_same_thread=False)
c = conn.cursor()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = account_c.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):  # Encode password to bytes
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Encode password to bytes
        try:
            account_c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            account_conn.commit()
            flash('Account created successfully!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different username.')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

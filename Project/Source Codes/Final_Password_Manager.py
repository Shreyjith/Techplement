import argparse
import bcrypt
import sqlite3
import maskpass
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import smtplib
import random
from prettytable import PrettyTable
import string
import secrets
import sys

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

c.execute('''
CREATE TABLE IF NOT EXISTS backup (
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

privacy="""\nPrivacy Policy:
Your data is encrypted and securely stored. We comply with GDPR and CCPA regulations.
You have the right to access, modify, and delete your data. Contact us for any privacy-related concerns.\n"""

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()
    return decrypted_data

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def OTP_Generation(username, user_email):
    global privacy
    OTP = "".join([str(random.randint(0, 9)) for i in range(4)])
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("py07otp@gmail.com", "iuln snfr xqiz ewnf")
    subject = "Your OTP Code"
    body = f"Hello {username},\n\nYour OTP is: {OTP}\n\n{privacy}\n\nRegards,\nPY07 Team"
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("py07otp@gmail.com", user_email, msg)
    server.quit()
    return OTP

def greeting_email(username, user_email):
    global privacy
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("py07otp@gmail.com", "iuln snfr xqiz ewnf")
    subject = "Welcome to Password Manager"
    body = f"Hello {username},\n\nThank you for using Console Based Password Manager!\n\n{privacy}\n\nRegards,\nPY07 Team"
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("py07otp@gmail.com", user_email, msg)
    server.quit()

def check_pass(password):
    special_characters = string.punctuation
    has_digit = False
    has_lower = False
    has_special = False
    has_upper = False

    if len(password) < 8:
        print("Weak Password")
        return

    for char in password:
        if char.isupper():
            has_upper = True
        if char.islower():
            has_lower = True
        if char.isdigit():
            has_digit = True
        if char in special_characters:
            has_special = True

    if has_upper and has_lower and has_digit and has_special:
        print("Very Strong Password")
    elif has_upper and has_lower and has_digit:
        print("Strong Password")
    elif has_upper and has_lower and has_special:
        print("Moderately Strong Password")
    elif has_upper and has_lower:
        print("Moderate Password")
    else:
        print("Weak Password")

def generate_password(length=8, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    characters = ''
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    if not characters:
        raise ValueError("At least one character set must be selected")
    return ''.join(secrets.choice(characters) for i in range(length))

def add_password():
    site = input("Enter the site name: ")
    username = input("Enter the username: ")
    email = input("Enter the email address: ")
    #password = maskpass.askpass("Enter the password: ", mask="*")

    pass_choice = input("Generate a password? (y/n): ")
    if pass_choice.lower() == "y":
        pass_length = int(input("Enter Length of Password (Minimum length should be 8 ): "))
        use_upper = input("Include uppercase letters? (y/n): ").lower() == 'y'
        use_lower = input("Include lowercase letters? (y/n): ").lower() == 'y'
        use_digits = input("Include digits? (y/n): ").lower() == 'y'
        use_special = input("Include special characters? (y/n): ").lower() == 'y'
        password = generate_password(pass_length, use_upper, use_lower, use_digits, use_special)
        print(f"Your generated password is: {password}")

    else:
        password = maskpass.askpass("Enter the password: ", mask="*")
        check_pass(password)  # Check password strength here
    category = input("Enter the category: ")
    tags = input("Enter tags (comma separated): ")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encrypted_password = encrypt_data(password)
    c.execute("INSERT INTO passwords (site, username, email, password, category, tags, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (site, username, email, encrypted_password, category, tags, last_updated))
    conn.commit()
    print("Password added successfully!")

def search_passwords(username, user_email):
    query = input("Enter the search query: ")
    c.execute("SELECT id, site, username, email, password, category, tags, last_updated FROM passwords WHERE site LIKE ? OR username LIKE ? OR email LIKE ? OR category LIKE ? OR tags LIKE ?", 
              (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    results = c.fetchall()
    table = PrettyTable()
    table.field_names = ["ID", "Site", "Username", "Email", "Password", "Category", "Tags", "Last Updated"]
    for result in results:
        result_list = list(result)
        result_list[4] = '*' * len(result_list[4])  # Mask the password
        result_list[4] = result_list[4][:8]  # Compress encryption data to 8 characters
        table.add_row(result_list)
    print(table)
    view_password_by_id(username, user_email)

def view_password_by_id(username, user_email):
    id_to_view = input("Enter the ID of the password you want to view (or press Enter to skip): ")
    OTP = OTP_Generation(username, user_email)
    user_otp = input("An OTP has been sent to your registered email address.\nOTP: ")
    if OTP == user_otp:
        if id_to_view:
            c.execute("SELECT password FROM passwords WHERE id=?", (id_to_view,))
            result = c.fetchone()
            if result:
                decrypted_password = decrypt_data(result[0])
                print(f"The password for ID {id_to_view} is: {decrypted_password}")
            else:
                print("No entry found with the given ID.")

def edit_password():
    id_to_edit = input("Enter the ID of the entry you want to edit: ")
    c.execute("SELECT * FROM passwords WHERE id=?", (id_to_edit,))
    result = c.fetchone()
    if result:
        site = input(f"Enter the new site name [{result[1]}]: ") or result[1]
        username = input(f"Enter the new username [{result[2]}]: ") or result[2]
        email = input(f"Enter the new email address [{result[3]}]: ") or result[3]
        password = maskpass.askpass(f"Enter the new password [{decrypt_data(result[4])}]: ", mask="*") or decrypt_data(result[4])
        check_pass(password)  # Check password strength here
        category = input(f"Enter the new category [{result[5]}]: ") or result[5]
        tags = input(f"Enter the new tags (comma separated) [{result[6]}]: ") or result[6]
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        encrypted_password = encrypt_data(password)
        c.execute("UPDATE passwords SET site=?, username=?, email=?, password=?, category=?, tags=?, last_updated=? WHERE id=?",
                  (site, username, email, encrypted_password, category, tags, last_updated, id_to_edit))
        conn.commit()
        print("Password updated successfully!")
    else:
        print("No entry found with the given ID.")

def delete_password():
    ids_to_delete = input("Enter the IDs of the entries you want to delete (comma separated): ")
    ids_to_delete = [id.strip() for id in ids_to_delete.split(',')]
    for id_to_delete in ids_to_delete:
        c.execute("SELECT * FROM passwords WHERE id=?", (id_to_delete,))
        result = c.fetchone()
        if result:
            c.execute("DELETE FROM passwords WHERE id=?", (id_to_delete,))
            conn.commit()
            print(f"Password with ID {id_to_delete} deleted successfully!")
    else:
        print("No entry found with the given ID.")

def backup_data():
    c.execute("DELETE FROM backup")
    c.execute("INSERT INTO backup SELECT * FROM passwords")
    conn.commit()
    print("Backup created successfully!")

def sync_data():
    print("Syncing data...")
    c.execute("SELECT id, site, username, email, password, category, tags, last_updated FROM backup")
    synced_data = c.fetchall()
    table = PrettyTable()
    table.field_names = ["ID", "Site", "Username", "Email", "Password", "Category", "Tags", "Last Updated"]
    for data in synced_data:
        data_list = list(data)
        data_list[4] = '*' * len(data_list[4])  # Mask the password
        data_list[4] = data_list[4][:8]  # Compress encryption data to 8 characters
        table.add_row(data_list)
    print(table)

def restore_data():
    c.execute("DELETE FROM passwords")
    c.execute("INSERT INTO passwords SELECT * FROM backup")
    conn.commit()
    print("Data restored successfully!")

def password_manager(username,user_email):
    global privacy
    print(privacy)

    session_start_time = datetime.now()

    while True:
        current_time = datetime.now()
        if current_time - session_start_time > timedelta(seconds=300):
            print("Session timeout (5 minutes)")
            break

        print("""
                1 or add: Add Password,
                2 or search: search Password,
                3 or edit: Edit save password,
                4 or backup: save the password in cloud,
                5 or sync: List All save Passwords,
                6 or restore: Restore the password
                7 or delete. Delete Password,
                8 or logout: Exit the program
            """)
        choice = input("Enter your choice: ").lower()
        if current_time - session_start_time > timedelta(seconds=300):
            print("Session timeout (5 minutes)")
        session_start_time = datetime.now()  # Reset the timer after each user input
        if choice in ['1','add']:
            add_password()
        elif choice in ['2', 'search']:
            search_passwords(username, user_email)
        elif choice in ['3','edit']: 
            edit_password()
        elif choice in ['4','backup']:
            backup_data()
        elif choice in ['5','sync']:
            sync_data()
        elif choice in ['6','restore']:
            restore_data()
        elif choice in ['7','delete']:
            delete_password()
        elif choice in ['logout','8']:
            print("Logged out successfully!")
            print("Thank you for using Console Based Password Manager!")
            break
        else:
            print("Invalid choice. Please try again.")

def login():
    username = input("Username: ")
    password = maskpass.askpass("Password: ", mask="*")

    account_c.execute("SELECT password, email FROM users WHERE username=?", (username,))
    result = account_c.fetchone()

    if result and verify_password(password, result[0]):
        user_email = result[1]
        if user_email:
            OTP = OTP_Generation(username, user_email)
            print("An OTP has been sent to your registered email address.")
            should_continue=True

            while should_continue:
                user_otp = input("OTP: ")
                if user_otp == OTP:
                    print("Login Successfully")
                    password_manager(username,user_email)
                    greeting_email(username, user_email)
                    should_continue=False
                else:
                    print("Invalid OTP")
        else:
            print("Email not found for the user.")
    else:
        print("User Not Found!")

def create_account():
    username = input("Enter username: ")
    email = input("Enter email: ")
    if account_c.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        print("Username already exists. Please choose a different username.")
        return
    #password = maskpass.askpass("Enter password: ", mask="*")
    pass_choice = input("Generate a password? (y/n): ")
    if pass_choice.lower() == "y":
        pass_length = int(input("\nEnter Length of Password (Minimum length should be 8 ): "))
        use_upper = input("Include uppercase letters? (y/n): ").lower() == 'y'
        use_lower = input("Include lowercase letters? (y/n): ").lower() == 'y'
        use_digits = input("Include digits? (y/n): ").lower() == 'y'
        use_special = input("Include special characters? (y/n): ").lower() == 'y'
        password = generate_password(pass_length, use_upper, use_lower, use_digits, use_special)
        print(f"Your generated password is: {password}\n")

    else:
        password = maskpass.askpass("Enter the password: ", mask="*")
        check_pass(password)  # Check password strength here
    hashed_password = hash_password(password)
    account_c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed_password))
    account_conn.commit()
    print("Account created successfully!")

def main():

    parser = argparse.ArgumentParser(description="Password Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Create an account
    subparsers.add_parser('CreateAccount', help='Create a new account')

    # Login in an Existing Account
    subparsers.add_parser('Login', help='Login an existing account')
    
    args = parser.parse_args()

    if args.command == 'CreateAccount':
        create_account()
    elif args.command == 'Login':
        login()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# Close the database connections when the script ends
conn.close()
account_conn.close()

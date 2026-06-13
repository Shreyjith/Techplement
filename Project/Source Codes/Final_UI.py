import tkinter as tk
from tkinter import messagebox, simpledialog
import bcrypt
import sqlite3
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import smtplib
import random
import string
import secrets
from prettytable import PrettyTable

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

privacy = """\nPrivacy Policy:
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

def verify_otp(username, user_email):
    OTP = OTP_Generation(username, user_email)
    user_otp = simpledialog.askstring("OTP", "An OTP has been sent to your registered email address.\nOTP:")
    if OTP == user_otp:
        return True
    else:
        return False

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
        messagebox.showinfo("Password Strength", "Weak Password")
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
        messagebox.showinfo("Password Strength", "Very Strong Password")
    elif has_upper and has_lower and has_digit:
        messagebox.showinfo("Password Strength", "Strong Password")
    elif has_upper and has_lower and has_special:
        messagebox.showinfo("Password Strength", "Moderately Strong Password")
    elif has_upper and has_lower:
        messagebox.showinfo("Password Strength", "Moderate Password")
    else:
        messagebox.showinfo("Password Strength", "Weak Password")

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

def change_password():
    username = simpledialog.askstring("Change Password", "Enter your username:")
    account_c.execute("SELECT email FROM users WHERE username=?", (username,))
    result = account_c.fetchone()
    if result and verify_otp(username, result[0]):
        new_password = simpledialog.askstring("Change Password", "Enter your new password:", show='*')
        check_pass(new_password)
        hashed_password = hash_password(new_password)
        account_c.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
        account_conn.commit()
        messagebox.showinfo("Success", "Password changed successfully!")
    else:
        messagebox.showinfo("Error", "Invalid username or OTP verification failed.")

def delete_account():
    username = simpledialog.askstring("Delete Account", "Enter your username:")
    account_c.execute("SELECT email FROM users WHERE username=?", (username,))
    result = account_c.fetchone()
    if result and verify_otp(username, result[0]):
        account_c.execute("DELETE FROM users WHERE username=?", (username,))
        account_conn.commit()
        messagebox.showinfo("Success", "Account deleted successfully!")
    else:
        messagebox.showinfo("Error", "Invalid username or OTP verification failed.")


def add_password():
    site = simpledialog.askstring("Input", "Enter the site name:")
    username = simpledialog.askstring("Input", "Enter the username:")
    email = simpledialog.askstring("Input", "Enter the email address:")

    pass_choice = messagebox.askyesno("Generate Password", "Generate a password?")
    if pass_choice:
        pass_length = simpledialog.askinteger("Input", "Enter Length of Password (Minimum length should be 8):")
        use_upper = messagebox.askyesno("Input", "Include uppercase letters?")
        use_lower = messagebox.askyesno("Input", "Include lowercase letters?")
        use_digits = messagebox.askyesno("Input", "Include digits?")
        use_special = messagebox.askyesno("Input", "Include special characters?")
        password = generate_password(pass_length, use_upper, use_lower, use_digits, use_special)
        messagebox.showinfo("Generated Password", f"Your generated password is: {password}")
    else:
        password = simpledialog.askstring("Input", "Enter the password:", show='*')
        check_pass(password)

    category = simpledialog.askstring("Input", "Enter the category:")
    tags = simpledialog.askstring("Input", "Enter tags (comma separated):")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encrypted_password = encrypt_data(password)
    c.execute("INSERT INTO passwords (site, username, email, password, category, tags, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (site, username, email, encrypted_password, category, tags, last_updated))
    conn.commit()
    messagebox.showinfo("Success", "Password added successfully!")

def search_passwords(username, user_email):
    query = simpledialog.askstring("Input", "Enter the search query:")
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
    messagebox.showinfo("Search Results", table.get_string())
    view_password_by_id(username, user_email)

def view_password_by_id(username, user_email):
    id_to_view = simpledialog.askstring("Input", "Enter the ID of the password you want to view (or press Enter to skip):")
    if id_to_view:
        if verify_otp(username, user_email):
            c.execute("SELECT password FROM passwords WHERE id=?", (id_to_view,))
            result = c.fetchone()
            if result:
                decrypted_password = decrypt_data(result[0])
                messagebox.showinfo("Password", f"The password for ID {id_to_view} is: {decrypted_password}")
            else:
                messagebox.showinfo("Error", "No entry found with the given ID.")
        else:
            messagebox.showinfo("Error", "OTP verification failed.")

def edit_password():
    id_to_edit = simpledialog.askstring("Input", "Enter the ID of the entry you want to edit:")
    c.execute("SELECT * FROM passwords WHERE id=?", (id_to_edit,))
    result = c.fetchone()
    if result:
        site = simpledialog.askstring("Input", f"Enter the new site name [{result[1]}]:", initialvalue=result[1])
        username = simpledialog.askstring("Input", f"Enter the new username [{result[2]}]:", initialvalue=result[2])
        email = simpledialog.askstring("Input", f"Enter the new email address [{result[3]}]:", initialvalue=result[3])
        password = simpledialog.askstring("Input", "Enter the new password (leave blank to keep current):", show='*')
        if not password:
            password = decrypt_data(result[4])
        else:
            check_pass(password)
        category = simpledialog.askstring("Input", f"Enter the new category [{result[5]}]:", initialvalue=result[5])
        tags = simpledialog.askstring("Input", f"Enter the new tags [{result[6]}]:", initialvalue=result[6])
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        encrypted_password = encrypt_data(password)
        c.execute("UPDATE passwords SET site=?, username=?, email=?, password=?, category=?, tags=?, last_updated=? WHERE id=?",
                  (site, username, email, encrypted_password, category, tags, last_updated, id_to_edit))
        conn.commit()
        messagebox.showinfo("Success", "Password updated successfully!")
    else:
        messagebox.showinfo("Error", "No entry found with the given ID.")

def delete_password():
    id_to_delete = simpledialog.askstring("Input", "Enter the ID of the entry you want to delete:")
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
    if confirm:
        c.execute("DELETE FROM passwords WHERE id=?", (id_to_delete,))
        conn.commit()
        messagebox.showinfo("Success", "Password deleted successfully!")

def backup_database():
    c.execute("INSERT INTO backup SELECT * FROM passwords")
    conn.commit()
    messagebox.showinfo("Success", "Database backup created successfully!")

def add_user():
    username = simpledialog.askstring("Input", "Enter a username:")
    email = simpledialog.askstring("Input", "Enter an email address:")
    password = simpledialog.askstring("Input", "Enter a password:", show='*')
    check_pass(password)
    hashed_password = hash_password(password)
    try:
        account_c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                          (username, email, hashed_password))
        account_conn.commit()
        greeting_email(username, email)
        messagebox.showinfo("Success", "User added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showinfo("Error", "Username already exists!")

def verify_user():
    username = simpledialog.askstring("Input", "Enter your username:")
    password = simpledialog.askstring("Input", "Enter your password:", show='*')
    account_c.execute("SELECT password, email FROM users WHERE username=?", (username,))
    result = account_c.fetchone()
    if result and verify_password(password, result[0]):
        if verify_otp(username, result[1]):
            messagebox.showinfo("Success", "Login successful!")
            open_main_menu(username, result[1])
    else:
        messagebox.showinfo("Error", "Invalid username or password!")

def open_main_menu(username, user_email):
    main_menu = tk.Tk()
    main_menu.title("Password Manager")
    main_menu.geometry("1920x1080")
    main_menu.configure(bg="#F0F8FF")

    title_label = tk.Label(main_menu, text="Password Manager", font=("Helvetica", 24, "bold"), bg="#F0F8FF")
    title_label.pack(pady=20)

    button_style = {
        "font": ("Helvetica", 14),
        "bg": "#4682B4",
        "fg": "white",
        "activebackground": "#5F9EA0",
        "activeforeground": "white",
        "width": 20,
        "height": 2,
        "bd": 3
    }

    add_button = tk.Button(main_menu, text="Add Password", command=add_password, **button_style)
    add_button.pack(pady=10)

    search_button = tk.Button(main_menu, text="Retrieve Password", command=lambda: search_passwords(username, user_email), **button_style)
    search_button.pack(pady=10)

    edit_button = tk.Button(main_menu, text="Edit Password", command=edit_password, **button_style)
    edit_button.pack(pady=10)

    delete_button = tk.Button(main_menu, text="Delete Password", command=delete_password, **button_style)
    delete_button.pack(pady=10)

    backup_button = tk.Button(main_menu, text="Backup Database", command=backup_database, **button_style)
    backup_button.pack(pady=10)

    footer_label = tk.Label(main_menu, text="Project done by PY07 Team", font=("Helvetica", 12), bg="#F0F8FF")
    footer_label.pack(side="bottom", pady=20)

    main_menu.mainloop()

# Initial user verification window
root = tk.Tk()
root.title("Login")
root.geometry("1920x1080")
root.configure(bg="#F0F8FF")

title_label = tk.Label(root, text="Password Manager Login", font=("Times New Roman", 24, "bold"), bg="#F0F8FF")
title_label.pack(pady=20)

button_style = {
    "font": ("Helvetica", 14, "bold"),
    "bg": "#4CAF50",  # Green background
    "fg": "white",  # White text
    "activebackground": "#45A049",  # Darker green for active button
    "activeforeground": "white",
    "width": 20,
    "height": 2,
    "bd": 5,  # Increase border width for a more pronounced button
    "relief": "raised",  # 3D effect
    "cursor": "hand2"  # Change cursor to hand on hover
}

while True:
    add_user_button = tk.Button(root, text="Signup", command=add_user, **button_style)
    add_user_button.pack(pady=8)

    verify_user_button = tk.Button(root, text="Login", command=verify_user, **button_style)
    verify_user_button.pack(pady=8)

    change_pass_button = tk.Button(root, text="Change Password", command=change_password, **button_style)
    change_pass_button.pack(pady=8)

    delete_user_button = tk.Button(root, text="Delete User", command=delete_account, **button_style)
    delete_user_button.pack(pady=8)

    exit_button = tk.Button(root, text="Exit", command=exit, **button_style)
    exit_button.pack(pady=10)

# Description label added below the buttons
    description_label = tk.Label(root, text="Password Manager by PY07 Team\n"
                                            "The PY07 team's Password Manager is a secure and user-friendly application designed to store and manage your passwords efficiently. \nWith a strong emphasis on security and ease of use, this tool allows users to add, retrieve, edit, and delete passwords with just a few clicks.\n\n"
                                            "Key Features:\n"
                                            "- Secure Encryption: Your data is encrypted using state-of-the-art technology to ensure your passwords are safe from unauthorized access.\n"
                                            "- User Authentication: Robust user authentication with OTP verification to protect your account.\n"
                                            "- Password Generation: Generate strong, customizable passwords to enhance your online security.\n"
                                            "- Backup & Recovery: Create backups of your password database to prevent data loss.\n"
                                            "- User-Friendly Interface: An intuitive and attractive interface designed for easy navigation and accessibility.\n"
                                            "\n"
                                            "Project Team\n"
                                            "This project was meticulously crafted by the PY07 team, dedicated to delivering a reliable and secure password management solution. \nWe prioritize user privacy and security, complying with GDPR and CCPA regulations to protect your personal data.",
                                font=("Times New Roman", 14), bg="#F0F8FF")
    description_label.pack(pady=10,side="bottom",anchor="center")

    footer_label = tk.Label(root, text="Project done by PY07 Team", font=("Helvetica", 12), bg="#F0F8FF")
    footer_label.pack(side="bottom", pady=20)

    root.mainloop()

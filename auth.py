import streamlit as st
import hashlib
import json
import os
from datetime import datetime

USER_DATA_FILE = "users.json"

# --- UTILITIES --- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        # Create default user if file doesn't exist
        default_user = {
            "shatwik": {
                "password": hash_password("12903478"),
                "created_at": datetime.now().isoformat()
            }
        }
        save_users(default_user)
        return default_user
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --- REGISTRATION --- #
def register():
    st.subheader("📝 Create Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not new_user or not new_pass or not confirm_pass:
            st.error("All fields are required.")
            return

        if new_pass != confirm_pass:
            st.error("Passwords do not match.")
            return

        users = load_users()
        if new_user in users:
            st.error("Username already exists.")
            return

        users[new_user] = {
            "password": hash_password(new_pass),
            "created_at": datetime.now().isoformat()
        }
        save_users(users)
        st.success("✅ Registration successful! You can now log in.")

# --- PASSWORD RESET --- #
def reset_password():
    st.subheader("🔐 Reset Password")
    user = st.text_input("Username")
    old_pass = st.text_input("Old Password", type="password")
    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password"):
        users = load_users()
        if user not in users or users[user]["password"] != hash_password(old_pass):
            st.error("Invalid username or old password.")
            return

        if new_pass != confirm_pass:
            st.error("New passwords do not match.")
            return

        users[user]["password"] = hash_password(new_pass)
        save_users(users)
        st.success("🔁 Password reset successfully!")

# --- LOGIN --- #
def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username]["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid credentials.")

# --- AUTH FLOW CONTROLLER --- #
def auth_flow():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.title("🔐 User Access")
        action = st.sidebar.radio("Choose an action", ["Login", "Register", "Reset Password"])

        if action == "Login":
            login()
        elif action == "Register":
            register()
        elif action == "Reset Password":
            reset_password()

        st.stop()

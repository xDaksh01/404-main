import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from users import USERS  # Import default users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = {}
    # Load default users first
    for username, password in USERS.items():
        users[username] = {
            "password": hash_password(password),
            "created_at": datetime.now().isoformat()
        }
    return users

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
            st.rerun()
        else:
            st.error("Invalid credentials.")

def auth_flow():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.title("🔐 User Access")
        login()
        st.stop()
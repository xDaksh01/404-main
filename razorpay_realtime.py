import requests
import streamlit as st
import pandas as pd
import time
from datetime import datetime

def start_realtime_tracking():
    user_key = st.session_state.razorpay_key
    user_secret = st.session_state.razorpay_secret
    seen_ids = set()
    while True:
        try:
            response = requests.get(
                "https://api.razorpay.com/v1/payments",
                auth=( user_key , user_secret )
            )
            data = response.json()["items"]
            new_rows = []
            for item in data:
                if item["id"] not in seen_ids and item["status"] == "captured":
                    seen_ids.add(item["id"])
                    new_rows.append({
                        "payment_id": item["id"],
                        "amount": item["amount"] / 100,
                        "app": item.get("description", "Unknown"),
                        "datetime": pd.to_datetime(item["created_at"], unit="s"),
                        "category": ""
                    })
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                try:
                    existing_df = pd.read_csv("razorpay_payments.csv")
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                except FileNotFoundError:
                    combined_df = pd.DataFrame(new_rows)
                combined_df.to_csv("razorpay_payments.csv", index=False)
        except Exception as e:
            print("Error fetching Razorpay data:", e)
        time.sleep(1)
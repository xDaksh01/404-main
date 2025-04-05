import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chatbot import chat_with_bot
from nudges import get_gamified_nudges, get_category_warnings
import hashlib
import os
from auth import auth_flow
import time
import numpy as np
from sklearn.linear_model import LinearRegression

# --- PAGE CONFIG --- #
st.set_page_config(page_title="AI Finance Assistant", layout="wide")

# --- DARK THEME --- #
st.markdown("""
    <style>
    /* Dark theme colors */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stPlotlyChart, .stpyplot {
        background-color: #1E1E1E !important;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .st-bx {
        background-color: #1E1E1E;
    }
    .st-eb {
        background-color: #2D2D2D;
    }
    div[data-testid="stMetricValue"] {
        color: #6C63FF;
    }
    button[data-testid="baseButton-secondary"] {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF;
    }
    .stProgress > div > div {
        background-color: #6C63FF;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION --- #
auth_flow()

# --- AUTHENTICATION --- #
auth_flow()

# --- LOADING SCREEN --- #
with st.spinner("🧙‍♂️ Summoning your Gringotts vault... Please wait..."):
    time.sleep(2)

# --- LOAD DATA --- #
@st.cache_data
def load_data():
    df = pd.read_csv("mock_transactions_detailed.csv", parse_dates=["datetime"])
    return df

st.sidebar.subheader("📁 Upload Your Transactions (CSV)")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["datetime"])
    st.success("✅ File uploaded and loaded successfully!")
else:
    df = load_data()

# Validate CSV format
expected_cols = {"datetime", "amount", "category", "type"}
if not expected_cols.issubset(df.columns):
    st.error("❌ Uploaded file is missing required columns. Using default dataset.")
    df = load_data()

# --- TITLE --- #
st.title("💰 AI Finance Assistant Dashboard")

# --- SIDEBAR FILTERS --- #
st.sidebar.header("📊 Filters")
selected_type = st.sidebar.multiselect("Type of Expense", df['type'].unique(), default=df['type'].unique())
selected_category = st.sidebar.multiselect("Category", df['category'].unique(), default=df['category'].unique())
date_range = st.sidebar.date_input("Date Range", [df["datetime"].min().date(), df["datetime"].max().date()])

# --- BUDGET SETTING --- #
st.sidebar.subheader("🎯 Monthly Budget")
if "budget" not in st.session_state:
    st.session_state.budget = 10000
new_budget = st.sidebar.number_input("Set your budget (₹)", min_value=0, value=st.session_state.budget, step=500)
if new_budget != st.session_state.budget:
    st.session_state.budget = new_budget
    st.sidebar.success(f"Budget updated to ₹{new_budget}")

# --- CATEGORY-WISE BUDGET SETTING --- #
st.sidebar.subheader("🎯 Category Budgets")
category_budgets = {}
for cat in df['category'].unique():
    category_budgets[cat] = st.sidebar.number_input(f"{cat} Budget (₹)", min_value=0, value=1000, step=100)

# --- FILTERED DATA --- #
filtered_df = df[
    (df["type"].isin(selected_type)) &
    (df["category"].isin(selected_category)) &
    (df["datetime"].dt.date >= date_range[0]) &
    (df["datetime"].dt.date <= date_range[1])
]

# --- SUMMARY METRICS --- #
st.subheader("📈 Quick Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"₹{filtered_df['amount'].sum():,.2f}")
col2.metric("Transactions", f"{len(filtered_df)}")
col3.metric("Avg. per Transaction", f"₹{filtered_df['amount'].mean():,.2f}")

# --- BUDGET PROGRESS --- #
current_month = pd.Timestamp.now().strftime('%Y-%m')
df_this_month = filtered_df[filtered_df["datetime"].dt.to_period('M').astype(str) == current_month]
spent_this_month = df_this_month["amount"].sum()
budget = st.session_state.budget
progress = min(spent_this_month / budget, 1.0)

st.subheader("📊 Monthly Budget Progress")
st.progress(progress)
col1, col2 = st.columns(2)
col1.metric("Spent This Month", f"₹{spent_this_month:,.0f}")
col2.metric("Remaining Budget", f"₹{budget - spent_this_month:,.0f}")

# --- CATEGORY-WISE SPENT & REMAINING --- #
st.subheader("🧾 Category-wise Budget Tracking")
fig, ax = plt.subplots(figsize=(12, 7))
categories = []
spent_amounts = []
budgets = []

for cat in df['category'].unique():
    cat_spent = df_this_month[df_this_month['category'] == cat]['amount'].sum()
    cat_budget = category_budgets.get(cat, 0)
    categories.append(cat)
    spent_amounts.append(cat_spent)
    budgets.append(cat_budget)

y_pos = np.arange(len(categories))
# Custom color palette
budget_color = '#E3E3E3'
spent_color = '#6C63FF'

# Add background grid with custom style
ax.grid(True, axis='x', linestyle='--', alpha=0.3, zorder=0)
ax.set_axisbelow(True)

# Plot bars with enhanced styling
ax.barh(y_pos, budgets, alpha=0.5, color=budget_color, label='Budget', height=0.6, zorder=2)
ax.barh(y_pos, spent_amounts, alpha=0.85, color=spent_color, label='Spent', height=0.6, zorder=3)

# Customize axis and labels
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=10, fontweight='bold')
ax.set_xlabel('Amount (₹)', fontsize=11, fontweight='bold')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add value labels on bars
for i, (spent, budget) in enumerate(zip(spent_amounts, budgets)):
    if spent > 0:
        ax.text(spent, i, f' ₹{spent:,.0f}', va='center', fontsize=9)
    if budget > 0:
        ax.text(budget, i, f' ₹{budget:,.0f}', va='center', fontsize=9, alpha=0.6)

# Enhance legend
ax.legend(loc='upper right', frameon=False, fontsize=10)

# Set background color
ax.set_facecolor('#1E1E1E')
fig.patch.set_facecolor('#1E1E1E')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')

plt.tight_layout()
st.pyplot(fig)

# Add custom CSS for the container
st.markdown("""
    <style>
    .stPlotlyChart, .stpyplot {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- EXPENSE FORECASTING --- #
st.subheader("📉 Expense Forecasting")
monthly_expenses = df.groupby(df["datetime"].dt.to_period("M"))['amount'].sum().reset_index()
monthly_expenses['datetime'] = monthly_expenses['datetime'].dt.to_timestamp()
monthly_expenses['month_num'] = range(1, len(monthly_expenses) + 1)

if len(monthly_expenses) >= 2:
    X = monthly_expenses[['month_num']]
    y = monthly_expenses['amount']
    model = LinearRegression()
    model.fit(X, y)
    next_month = np.array([[monthly_expenses['month_num'].max() + 1]])
    prediction = model.predict(next_month)[0]

    st.info(f"📅 Predicted expense for next month: ₹{prediction:,.0f}")

    if prediction > budget:
        st.warning("🚨 Your next month's expenses may exceed your set budget!")
else:
    st.info("📉 Not enough data to generate forecast.")

# --- CATEGORY-WISE FORECASTING --- #
st.subheader("🔍 Category-wise Expense Forecasting")
future_forecasts = {}
for cat in df['category'].unique():
    cat_df = df[df['category'] == cat]
    monthly_cat = cat_df.groupby(cat_df["datetime"].dt.to_period("M"))['amount'].sum().reset_index()
    if len(monthly_cat) < 2:
        continue
    monthly_cat['datetime'] = monthly_cat['datetime'].dt.to_timestamp()
    monthly_cat['month_num'] = range(1, len(monthly_cat) + 1)
    X_cat = monthly_cat[['month_num']]
    y_cat = monthly_cat['amount']
    model = LinearRegression()
    model.fit(X_cat, y_cat)
    next_month_cat = np.array([[monthly_cat['month_num'].max() + 1]])
    forecast_cat = model.predict(next_month_cat)[0]
    future_forecasts[cat] = forecast_cat

for cat, forecast in future_forecasts.items():
    cat_budget = category_budgets.get(cat, 0)
    forecast_msg = f"📌 **{cat}**: Forecasted ₹{forecast:.0f} / Budget ₹{cat_budget}"
    if forecast > cat_budget:
        st.warning(f"🚨 {forecast_msg} — Likely to overspend!")
    else:
        st.info(f"✅ {forecast_msg} — Looks safe.")

# --- GAMIFIED BADGES --- #
def get_savings_badge(savings):
    if 1 <= savings <= 100:
        return "🥉 Bronze Saver - Good start!"
    elif 101 <= savings <= 500:
        return "🥈 Silver Saver - Nice job!"
    elif 501 <= savings <= 1000:
        return "🥇 Gold Saver - Great work!"
    elif 1001 <= savings <= 2000:
        return "🏅 Platinum Saver - You're killing it!"
    elif savings > 2000:
        return "💎 Diamond Saver - Legendary savings!"
    return None

savings = budget - spent_this_month
badge = get_savings_badge(savings)
if badge:
    st.success(f"🏆 {badge}")

# --- GAMIFIED NUDGES --- #
st.subheader("🏆 Achievement Nudges")
badges = get_gamified_nudges(df_this_month, budget)
for badge in badges:
    st.success(badge)

# --- CATEGORY BUDGET WARNINGS --- #
st.subheader("⚠️ Category Budget Warnings")
category_warnings = get_category_warnings(df_this_month, category_budgets)
for warning in category_warnings:
    st.warning(warning)

# --- MONTHLY SPENDING --- #
st.subheader("📅 Monthly Spending")
filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
monthly = filtered_df.groupby("month")["amount"].sum().sort_index()
st.bar_chart(monthly)

# --- WEEKLY SPENDING --- #
st.subheader("📆 Weekly Spending")
filtered_df['week'] = filtered_df['datetime'].dt.isocalendar().week
weekly = filtered_df.groupby("week")["amount"].sum().sort_index()
st.line_chart(weekly)

# --- DAILY HEATMAP --- #
st.subheader("🕒 Daily Spending Heatmap")
heatmap_data = filtered_df.copy()
heatmap_data['date'] = heatmap_data['datetime'].dt.date
heatmap = heatmap_data.groupby(['date'])['amount'].sum().reset_index()
heatmap['date'] = pd.to_datetime(heatmap['date'])
fig, ax = plt.subplots(figsize=(12, 4))
sns.lineplot(x='date', y='amount', data=heatmap, ax=ax)
ax.set_title("Daily Spending Over Time")
st.pyplot(fig)

# --- CATEGORY SPENDING --- #
st.subheader("📂 Spending by Category")
cat_data = filtered_df.groupby("category")["amount"].sum().sort_values(ascending=False)
st.bar_chart(cat_data)

# --- TIME OF DAY SPENDING --- #
st.subheader("⏰ Spending by Time of Day")
filtered_df['hour'] = filtered_df['datetime'].dt.hour
hourly = filtered_df.groupby('hour')['amount'].sum()
st.line_chart(hourly)

# --- CHATBOT --- #
st.subheader("💬 Ask Your Assistant")
user_input = st.chat_input("Talk to your finance assistant (e.g., 'How much did I spend on shopping in Feb 2024?')")
if user_input:
    response = chat_with_bot(user_input, filtered_df)
    st.success(response)

# --- OPTIONAL ENHANCEMENTS SECTION --- #
with st.expander("🛠 Optional Enhancements You Can Add"):
    st.markdown("""
    | Feature | Description |
    |--------|-------------|
    | 🔐 **Login System** | Secure access with username/password using hashed passwords |
    | 📥 **CSV Upload** | Upload your **own bank statements** in `.csv` format and view custom insights |
    | 🧠 **Smarter Chatbot** | Use **OpenAI/GPT** to answer complex queries like "What were my top 3 unnecessary expenses last month?" |
    | 🎯 **Budget Goals** | Set your own **monthly budget** and track progress visually |
    | 🏆 **Gamified Nudges** | Earn fun **badges/achievements** when you hit savings goals |
    | 📤 **Export Reports** | Export your data and insights to **PDF or Excel** format |
    """)
    st.info("💡 Let me know which one you want to build next and I’ll guide you step by step!")
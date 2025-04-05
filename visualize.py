import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Apply Seaborn theme
sns.set(style="whitegrid")

# Load and clean data
df = pd.read_csv("mock_transactions.csv")
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M').astype(str)
df['week'] = df['date'].dt.strftime('%G-W%V')

# Line Chart – Monthly Spending Trend
def plot_monthly_trend():
    monthly = df.groupby('month')['amount'].sum().reset_index()
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=monthly, x='month', y='amount', marker='o', color='royalblue')
    plt.title("📈 Monthly Spending Trend", fontsize=14)
    plt.xlabel("Month")
    plt.ylabel("Total Spending (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Pie Chart – This Week's Spending by Category
def plot_weekly_pie():
    current_week = datetime.now().strftime('%G-W%V')
    weekly_df = df[df['week'] == current_week]
    if weekly_df.empty:
        print("⚠️ No transactions for this week.")
        return
    pie_data = weekly_df.groupby('category')['amount'].sum()
    plt.figure(figsize=(6, 6))
    pie_data.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title(f"🧁 Spending by Category – {current_week}")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

# Bar Chart – Total Spent per Category (All Time)
def plot_category_spending():
    category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False).reset_index()
    plt.figure(figsize=(8, 5))
    sns.barplot(data=category_data, x='amount', y='category', palette='viridis')
    plt.title("📊 Total Spending by Category", fontsize=14)
    plt.xlabel("Total Amount (₹)")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.show()

# Run visualizations
if __name__ == "__main__":
    print("✅ Generating visualizations...")
    plot_monthly_trend()
    plot_weekly_pie()
    plot_category_spending()

import pandas as pd

def get_gamified_nudges(df, budget, category_budgets=None):
    nudges = []

    if df.empty:
        return ["📭 No transactions found for this period. Try adjusting your filters!"]

    total_spent = df["amount"].sum()
    total_saved = max(budget - total_spent, 0)
    num_txns = len(df)

    # 🏅 Budget milestones
    if total_spent < budget * 0.5:
        nudges.append("🏅 Great job! You've spent less than 50% of your budget!")
    elif total_spent < budget:
        nudges.append("✅ You're within your budget! Keep it going!")
    else:
        nudges.append("🚨 You've exceeded your budget. Let’s get back on track!")

    # 🔥 Low-spend streaks
    df['date'] = df['datetime'].dt.date
    daily_spend = df.groupby("date")["amount"].sum()
    low_spend_days = (daily_spend < 200).sum()
    if low_spend_days >= 3:
        nudges.append(f"🔥 You had {low_spend_days} low-spend days! That’s solid discipline!")

    # 🎯 Single category dominance
    cat_spend = df.groupby("category")["amount"].sum()
    if not cat_spend.empty:
        top_category = cat_spend.idxmax()
        top_amount = cat_spend.max()
        if top_amount / total_spent > 0.4:
            nudges.append(f"🧐 Most of your spend went to **{top_category}**. Consider dialing it down.")

    # 🎖️ Consistent saving habit
    daily_average = total_spent / len(daily_spend)
    if daily_average < 500:
        nudges.append("🎖️ You’re averaging under ₹500/day. That’s budget champion behavior!")

    # 🧠 Spending awareness
    high_txn_days = (daily_spend > 2000).sum()
    if high_txn_days > 2:
        nudges.append(f"⚠️ You had {high_txn_days} high-spend days. Watch out for spikes!")

    # 🏆 Saving badges
    if total_saved >= 2000:
        nudges.append("💎 You earned the **Diamond** badge for saving ₹2000+!")
    elif total_saved >= 1001:
        nudges.append("🏆 You earned the **Platinum** badge for saving ₹1001–2000!")
    elif total_saved >= 501:
        nudges.append("🥇 You earned the **Gold** badge for saving ₹501–1000!")
    elif total_saved >= 101:
        nudges.append("🥈 You earned the **Silver** badge for saving ₹101–500!")
    elif total_saved >= 1:
        nudges.append("🥉 You earned the **Bronze** badge for saving ₹1–100!")

    return nudges


def get_category_warnings(df, category_budgets):
    warnings = []

    if df.empty:
        return warnings

    df['month'] = df['datetime'].dt.to_period('M')
    monthly_df = df[df['month'] == pd.Timestamp.now().to_period('M')]

    cat_spending = monthly_df.groupby("category")["amount"].sum()

    for category, spent in cat_spending.items():
        budget = category_budgets.get(category, None)
        if budget:
            ratio = spent / budget
            if ratio > 0.6:
                warnings.append(f"⚠️ You've spent ₹{spent:.0f} in **{category}**, which is over 60% of its ₹{budget} budget!")

    return warnings

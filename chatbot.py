import pandas as pd
import datetime
from dateutil.parser import parse

# Helper functions
def extract_year(text):
    for token in text.split():
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None

def extract_month(text):
    months = {m.lower(): i for i, m in enumerate([
        "", "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ])}
    for word in text.split():
        if word.lower() in months:
            return months[word.lower()]
    return None

def get_week_number():
    return datetime.datetime.now().isocalendar()[1]

def chat_with_bot(user_input, df):
    user_input = user_input.lower()

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])

    # 1️⃣ Category-based spending
    if "how much did i spend on" in user_input:
        for category in df['category'].unique():
            if category.lower() in user_input:
                total = df[df['category'].str.lower() == category.lower()]['amount'].sum()
                return f"💸 You spent ₹{total:.2f} on {category} overall."

    # 2️⃣ Yearly/Monthly spending
    elif "how much did i spend in" in user_input:
        year = extract_year(user_input)
        month = extract_month(user_input)
        filtered = df
        if year:
            filtered = filtered[filtered['date'].dt.year == year]
        if month:
            filtered = filtered[filtered['date'].dt.month == month]

        total = filtered['amount'].sum()
        if not filtered.empty:
            date_label = f"{month and datetime.date(1900, month, 1).strftime('%B')} {year}" if month else str(year)
            return f"📆 You spent ₹{total:.2f} in {date_label}."
        else:
            return "📂 No spending data found for that period."

    # 3️⃣ Weekly summary
    elif "weekly spending" in user_input or "this week" in user_input:
        week_num = get_week_number()
        current_week = df[df['date'].dt.isocalendar().week == week_num]
        if current_week.empty:
            return "📭 No spending activity recorded this week."

        summary = current_week.groupby("category")["amount"].sum().reset_index()
        response = f"📊 Spending Summary for Week {week_num}:\n"
        for _, row in summary.iterrows():
            response += f"• {row['category']}: ₹{row['amount']:.2f}\n"
        return response

    # 4️⃣ Nudges & tips
    elif "nudge" in user_input or "tip" in user_input:
        food = df[df['category'] == "Food"]["amount"].sum()
        shopping = df[df['category'] == "Shopping"]["amount"].sum()
        total = df["amount"].sum()

        tips = []
        if food > 2000:
            tips.append("🍔 Try reducing food delivery — maybe meal prep this week?")
        if shopping > 3000:
            tips.append("🛍️ A no-spend weekend challenge could help!")
        if total > 10000:
            tips.append("💡 Consider setting a monthly budget to avoid overspending.")

        return "\n".join(tips) if tips else "✅ You're spending wisely! Keep it up!"

    # 5️⃣ General response
    else:
        return (
            "🤖 You can ask things like:\n"
            "- How much did I spend on Food?\n"
            "- Show me my weekly spending\n"
            "- How much did I spend in March 2024?\n"
            "- Give me a nudge to save\n"
        )

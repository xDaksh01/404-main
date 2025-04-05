import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define categories as needs and wants
categories = {
    'Groceries': 'need',
    'Rent': 'need',
    'Utilities': 'need',
    'Transport': 'need',
    'Healthcare': 'need',
    'Dining Out': 'want',
    'Shopping': 'want',
    'Entertainment': 'want',
    'Travel': 'want',
    'Food Delivery': 'want',
    'Subscriptions': 'want'
}

# Function to generate a single transaction
def generate_transaction(start_date, end_date):
    date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
    category = random.choice(list(categories.keys()))
    amount = round(random.uniform(100, 5000), 2)
    description = f"{category} expense"
    type_of_expense = categories[category]
    return {
        'datetime': date,
        'date': date.strftime('%Y-%m-%d'),
        'time': date.strftime('%H:%M:%S'),
        'month': date.strftime('%B %Y'),
        'week': f"Week {date.isocalendar()[1]}",
        'category': category,
        'amount': amount,
        'description': description,
        'type': type_of_expense
    }

# Generate 1000 transactions between Jan 2024 and April 2025
start = datetime(2024, 1, 1)
end = datetime(2025, 4, 5)
transactions = [generate_transaction(start, end) for _ in range(1000)]

# Create a DataFrame
df = pd.DataFrame(transactions)
df.sort_values(by="datetime", inplace=True)

# Save the data
df.to_csv("mock_transactions_detailed.csv", index=False)
print("✅ Dataset generated: mock_transactions_detailed.csv")

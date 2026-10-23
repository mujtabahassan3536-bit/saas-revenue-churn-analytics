import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

NUM_CUSTOMERS = 200
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 9, 1)

# ==========================================
# 1. GENERATE RAW DATA
# ==========================================

# Generate Customers
customers_data = []
industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Education']
for i in range(1, NUM_CUSTOMERS + 1):
    customers_data.append({
        'Customer_ID': f"CUST_{i:04d}",
        'Company_Name': fake.company(),
        'Industry': random.choice(industries),
        'Signup_Date': fake.date_between(start_date=START_DATE, end_date=END_DATE - timedelta(days=30))
    })
df_customers = pd.DataFrame(customers_data)

# Generate Subscription Events (New, Upgrade, Downgrade, Churn)
events_data = []
for idx, row in df_customers.iterrows():
    cid = row['Customer_ID']
    signup = row['Signup_Date']
    
    # Initial Signup Event
    initial_mrr = random.choice([50, 100, 200])
    events_data.append({
        'Event_ID': fake.uuid4(),
        'Customer_ID': cid,
        'Event_Type': 'New',
        'MRR_Delta': initial_mrr,
        'Event_Date': signup
    })
    
    # Random future event (50% chance of Expansion, Contraction, or Churn)
    if random.random() > 0.5:
        event_date = signup + timedelta(days=random.randint(30, 200))
        if event_date < END_DATE.date():
            event_type = random.choices(['Expansion', 'Contraction', 'Churn'], weights=[0.5, 0.2, 0.3])[0]
            
            if event_type == 'Expansion': mrr_delta = 50
            elif event_type == 'Contraction': mrr_delta = -50
            else: mrr_delta = -initial_mrr # Churn removes all MRR
            
            events_data.append({
                'Event_ID': fake.uuid4(),
                'Customer_ID': cid,
                'Event_Type': event_type,
                'MRR_Delta': mrr_delta,
                'Event_Date': event_date
            })

df_events = pd.DataFrame(events_data)

# Generate Product Usage Logs (with intentional missing data)
usage_data = []
for cid in df_customers['Customer_ID']:
    for month in range(1, 7): # Simulate 6 months of logs
        log_date = START_DATE + timedelta(days=month*30)
        usage_data.append({
            'Log_ID': fake.uuid4(),
            'Customer_ID': cid,
            'Log_Date': str(log_date.date()), # Intentionally string for parsing practice
            'Logins': random.randint(1, 50) if random.random() > 0.1 else np.nan, # 10% nulls
            'Features_Used': random.randint(1, 10) if random.random() > 0.15 else np.nan # 15% nulls
        })
df_usage = pd.DataFrame(usage_data)

# ==========================================
# 2. DATA CLEANING & VALIDATION (Day 1 Goals)
# ==========================================

print("--- Starting Data Cleaning ---")

# Parse Timestamps
df_customers['Signup_Date'] = pd.to_datetime(df_customers['Signup_Date'])
df_events['Event_Date'] = pd.to_datetime(df_events['Event_Date'])
df_usage['Log_Date'] = pd.to_datetime(df_usage['Log_Date'])
print("✓ Timestamps parsed to datetime objects.")

# Handle Null Values
# Fill missing logins with 0 (assuming no usage) and median for features used
df_usage['Logins'] = df_usage['Logins'].fillna(0)
df_usage['Features_Used'] = df_usage['Features_Used'].fillna(df_usage['Features_Used'].median())
print(f"✓ Nulls handled. Remaining nulls: {df_usage.isnull().sum().sum()}")

# Validate Revenue Deltas
total_revenue = df_events['MRR_Delta'].sum()
churn_revenue = df_events[df_events['Event_Type'] == 'Churn']['MRR_Delta'].sum()
print(f"✓ Total MRR generated across all time: ${total_revenue}")
print(f"✓ Total MRR lost to Churn: ${churn_revenue}")

# ==========================================
# 3. EXPORT TO CSV
# ==========================================
df_customers.to_csv('Customers.csv', index=False)
df_events.to_csv('Subscription_Events.csv', index=False)
df_usage.to_csv('Product_Usage_Logs.csv', index=False)
print("✓ Files exported successfully: Customers.csv, Subscription_Events.csv, Product_Usage_Logs.csv")

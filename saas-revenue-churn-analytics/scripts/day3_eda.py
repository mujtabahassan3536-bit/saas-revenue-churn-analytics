import pandas as pd

# Load all three datasets
df_customers = pd.read_csv('data/Customers.csv')
df_events = pd.read_csv('data/Subscription_Events.csv')
df_usage = pd.read_csv('data/Product_Usage_Logs.csv')

print("--- SaaS Analytics EDA Summary ---")

# 1. Customer Distribution by Industry
print("\n[1] Customers by Industry:")
print(df_customers['Industry'].value_counts())

# 2. Revenue Breakdown by Event Type
print("\n[2] Revenue Impact by Event Type:")
event_summary = df_events.groupby('Event_Type')['MRR_Delta'].agg(['count', 'sum'])
print(event_summary)

# 3. Account Health Score Distribution
print("\n[3] Latest Account Health Status (Usage Logs):")
# Taking the latest log for each customer to see current health
latest_usage = df_usage.sort_values('Log_Date').groupby('Customer_ID').last()
health_counts = latest_usage['Account_Health_Score'].value_counts()
print(health_counts)

# 4. Overall Churn Rate Calculation
total_customers = len(df_customers)
churned_customers = df_events[df_events['Event_Type'] == 'Churn']['Customer_ID'].nunique()
churn_rate = (churned_customers / total_customers) * 100
print(f"\n[4] Overall Churn Rate: {churn_rate:.2f}% ({churned_customers} out of {total_customers} customers)")
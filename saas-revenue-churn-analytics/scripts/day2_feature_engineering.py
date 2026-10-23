import pandas as pd
import numpy as np

# Load data
df_usage = pd.read_csv('data/Product_Usage_Logs.csv')
df_usage['Log_Date'] = pd.to_datetime(df_usage['Log_Date'])

# Feature Engineering: MoM Drop Ratio
df_usage = df_usage.sort_values(by=['Customer_ID', 'Log_Date'])
df_usage['Prev_Month_Logins'] = df_usage.groupby('Customer_ID')['Logins'].shift(1)

df_usage['MoM_Login_Ratio'] = np.where(
    df_usage['Prev_Month_Logins'] == 0, 
    1.0, 
    df_usage['Logins'] / df_usage['Prev_Month_Logins']
)
df_usage['MoM_Login_Ratio'] = df_usage['MoM_Login_Ratio'].fillna(1.0)

# Feature Engineering: Account Health Score
df_usage['Account_Health_Score'] = np.where(
    df_usage['Logins'] == 0, 
    20, 
    np.where(
        df_usage['MoM_Login_Ratio'] < 1.0, 
        50, 
        90
    )
)

# Export updated usage logs back to data folder
df_usage.to_csv('data/Product_Usage_Logs.csv', index=False)
print("✓ Day 2 Feature Engineering complete. Product_Usage_Logs.csv updated successfully.")
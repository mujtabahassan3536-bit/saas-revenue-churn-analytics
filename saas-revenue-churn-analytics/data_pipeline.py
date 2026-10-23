import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123",
    database="saas_sales_analytics"
)

query = """
    SELECT Log_ID, Customer_ID, Log_Date, Logins, Features_Used, Account_Health_Score 
    FROM product_usage_logs
"""
df = pd.read_sql(query, conn)

df['Log_Date'] = pd.to_datetime(df['Log_Date'])
df = df.sort_values(by=['Customer_ID', 'Log_Date'])

conn.close()

print(df.tail())
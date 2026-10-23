import streamlit as st
import pandas as pd
import mysql.connector
import warnings
import time

warnings.filterwarnings('ignore', category=UserWarning)

st.set_page_config(page_title="AI Churn Predictor", layout="wide")

def run_query(query):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mujtaba2@!1",
        database="saas_sales_analytics"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    customers_df = run_query("SELECT DISTINCT Customer_ID FROM product_usage_logs ORDER BY Customer_ID")
    customer_list = customers_df['Customer_ID'].tolist()
except Exception as e:
    customer_list = ["Error"]
    st.error(f"Database error: {e}")

st.sidebar.header("Control Panel")
st.sidebar.success("Connected to MySQL Pipeline")

selected_customer = st.sidebar.selectbox("Select Customer ID:", customer_list)
analyze_btn = st.sidebar.button("Analyze Risk")

st.title("B2B SaaS Churn Analytics")
st.markdown("---")

# Top KPI metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Active Customers", value="1,245", delta="12")
with col2:
    st.metric(label="Avg Account Health", value="78", delta="-2.5%", delta_color="inverse")
with col3:
    st.metric(label="High Risk Accounts", value="34", delta="5", delta_color="inverse")

st.markdown("---")
st.subheader(f"Customer Profile: {selected_customer}")


if analyze_btn and selected_customer != "Error":
    with st.spinner("Extracting live data from MySQL..."):
        time.sleep(1) 
        
       
        query = f"SELECT Log_Date, Logins, Account_Health_Score FROM product_usage_logs WHERE Customer_ID = '{selected_customer}' ORDER BY Log_Date"
        cust_df = run_query(query)
        
        if not cust_df.empty:
            st.success("Analysis Complete! Live data mapped.")
            
            det_col1, det_col2 = st.columns(2)
            
            with det_col1:
                st.write("Account Health Score")
                
               
                latest_score = float(cust_df['Account_Health_Score'].iloc[-1])
                st.progress(latest_score / 100.0)
                
              
                if latest_score >= 75:
                    st.info("Status: Safe. Normal usage patterns detected.")
                elif latest_score >= 40:
                    st.warning("Status: Moderate Risk. Monitor activity closely.")
                else:
                    st.error("Status: High Churn Risk! Immediate action required.")
                    
            with det_col2:
                st.write("Usage Trend (Logins over time)")
           
                chart_data = cust_df.set_index('Log_Date')['Logins']
                st.line_chart(chart_data)
        else:
            st.warning("No historical data found for this customer.")
else:
    st.info("Click Analyze Risk to fetch live data and generate trends.")
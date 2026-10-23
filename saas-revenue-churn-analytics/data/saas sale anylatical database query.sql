-- 1. Database Select Karein
USE saas_sales_analytics;


-- 1. Customers Dimension Table
CREATE TABLE Customers (
    Customer_ID VARCHAR(50) NOT NULL,
    Company_Name VARCHAR(255),
    Industry VARCHAR(100),
    Signup_Date DATE,
    PRIMARY KEY (Customer_ID)
) ENGINE=InnoDB;

-- 2. Subscription Events Fact Table
CREATE TABLE Subscription_Events (
    Event_ID VARCHAR(50) NOT NULL,
    Customer_ID VARCHAR(50),
    Event_Type VARCHAR(50),
    MRR_Delta DECIMAL(10, 2),
    Event_Date DATE,
    PRIMARY KEY (Event_ID),
    CONSTRAINT fk_customer_events 
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID)
) ENGINE=InnoDB;

-- 3. Product Usage Logs Fact Table
CREATE TABLE Product_Usage_Logs (
    Log_ID VARCHAR(50) NOT NULL,
    Customer_ID VARCHAR(50),
    Log_Date DATE,
    Logins INT,
    Features_Used INT,
    Prev_Month_Logins INT, -- (Correction applied: Changed DECIMAL to INT)
    MoM_Login_Ratio DECIMAL(10, 2),
    Account_Health_Score INT,
    PRIMARY KEY (Log_ID),
    CONSTRAINT fk_customer_usage 
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID)
) ENGINE=InnoDB;

-- ==========================================
-- SECTION C: BASIC VALIDATION QUERIES
-- ==========================================

SHOW TABLES;
SELECT * FROM Customers LIMIT 5;
SELECT COUNT(*) FROM Customers;
SELECT COUNT(*) FROM Product_Usage_Logs;

-- ==========================================
-- SECTION D: BUSINESS ANALYTICS QUERIES
-- ==========================================

-- Query 1: Un customers ko dhoondti hai jinki product usage drop ho chuki hai (Risk < 50)
SELECT 
    c.Customer_ID,
    c.Company_Name,
    c.Industry,
    p.Log_Date,
    p.Logins,
    p.MoM_Login_Ratio,
    p.Account_Health_Score
FROM Customers c
JOIN Product_Usage_Logs p ON c.Customer_ID = p.Customer_ID
WHERE p.Account_Health_Score <= 50
ORDER BY p.Account_Health_Score ASC, p.Log_Date DESC;

-- Query 2: Health Score ka distribution check karna
SELECT Account_Health_Score, COUNT(*) 
FROM Product_Usage_Logs 
GROUP BY Account_Health_Score;

-- Query 3: Advanced JOIN - Churn risk ke sath Revenue Impact (MRR_Delta) dekhna
SELECT 
    c.Company_Name, 
    c.Industry, 
    p.Account_Health_Score, 
    s.Event_Type,
    s.MRR_Delta AS Revenue_Impact
FROM Customers c
JOIN Product_Usage_Logs p 
    ON c.Customer_ID = p.Customer_ID
JOIN Subscription_Events s 
    ON c.Customer_ID = s.Customer_ID
WHERE p.Account_Health_Score <= 50
ORDER BY s.MRR_Delta ASC;

-- 1. Pehle database select karein
USE saas_sales_analytics;

-- 2. Check karein ke kon kon si tables ban chuki hain
SHOW TABLES;

-- 3. Customers table ka data dekhein (Shuru ke 100 records)
-- Is se aapko pata chalega ke Faker ne kon se naam aur industries generate ki hain
SELECT * FROM Customers LIMIT 100;

-- 4. Subscription Events ka data dekhein
-- Is se MRR_Delta aur Event_Types nazar aayenge
SELECT * FROM Subscription_Events LIMIT 100;

-- 5. Product Usage Logs ka data dekhein (Yeh sab se main table hai)
-- Yahan aapko apna calculate kiya hua Health Score aur MoM Ratio nazar aayega
SELECT * FROM Product_Usage_Logs LIMIT 100;

-- 6. Total Rows count karein (Yeh check karne ke liye ke Python ne total kitna data dala)
SELECT 
    (SELECT COUNT(*) FROM Customers) AS Total_Customers,
    (SELECT COUNT(*) FROM Subscription_Events) AS Total_Events,
    (SELECT COUNT(*) FROM Product_Usage_Logs) AS Total_Logs;

-- 7. Aapka banaya hua Master View (Jo actually aapki sab se bari achievement hai)
-- Yeh query aapko poore system ka nichor (summary) dikhayegi
SELECT 
    c.Company_Name, 
    c.Industry, 
    p.Account_Health_Score, 
    s.Event_Type,
    s.MRR_Delta AS Revenue_Impact
FROM Customers c
JOIN Product_Usage_Logs p 
    ON c.Customer_ID = p.Customer_ID
JOIN Subscription_Events s 
    ON c.Customer_ID = s.Customer_ID
ORDER BY p.Account_Health_Score ASC
LIMIT 100;


USE saas_sales_analytics;

SELECT 
    Customer_ID, 
    Event_Date, 
    Event_Type, 
    MRR_Delta AS Current_MRR,
    LAG(MRR_Delta, 1) OVER (
        PARTITION BY Customer_ID 
        ORDER BY Event_Date
    ) AS Previous_MRR
FROM 
    subscription_events;
    
    CREATE OR REPLACE VIEW view_customer_mrr_history AS
SELECT 
    Customer_ID, 
    Event_Date, 
    Event_Type, 
    MRR_Delta AS Current_MRR,
    LAG(MRR_Delta, 1) OVER (
        PARTITION BY Customer_ID 
        ORDER BY Event_Date
    ) AS Previous_MRR
FROM 
    subscription_events;
    
    
    WITH Monthly_Summary AS (
    SELECT 
        DATE_FORMAT(Event_Date, '%Y-%m') AS Revenue_Month,
        Event_Type,
        SUM(Current_MRR) AS Total_MRR
    FROM 
        view_customer_mrr_history
    GROUP BY 
        Revenue_Month, Event_Type
)
SELECT * 
FROM Monthly_Summary
ORDER BY Revenue_Month, Event_Type;


CREATE OR REPLACE VIEW view_monthly_mrr_summary AS
WITH Monthly_Summary AS (
    SELECT 
        DATE_FORMAT(Event_Date, '%Y-%m') AS Revenue_Month,
        Event_Type,
        SUM(Current_MRR) AS Total_MRR
    FROM 
        view_customer_mrr_history
    GROUP BY 
        Revenue_Month, Event_Type
)
SELECT * 
FROM Monthly_Summary;
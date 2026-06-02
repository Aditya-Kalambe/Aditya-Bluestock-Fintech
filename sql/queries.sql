-- 1. Top 5 Funds by Highest Current AUM
SELECT f.scheme_name, a.aum_crore, a.snapshot_date
FROM fact_aum a
JOIN dim_fund f ON a.amfi_code = f.amfi_code
ORDER BY a.aum_crore DESC
LIMIT 5;

-- 2. Average NAV Per Month for All Schemes
SELECT f.scheme_name, d.calendar_year, d.month_name, AVG(n.nav) as avg_monthly_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.nav_date = d.date_key
GROUP BY f.scheme_name, d.calendar_year, d.calendar_month;

-- 3. SIP Year-over-Year (YoY) Growth in Gross Inflow Volumes
WITH sip_yearly AS (
    SELECT d.calendar_year, SUM(t.amount) as total_sip_amount
    FROM fact_transactions t
    JOIN dim_date d ON t.transaction_date = d.date_key
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.calendar_year
)
SELECT curr.calendar_year, curr.total_sip_amount,
       ((curr.total_sip_amount - prev.total_sip_amount) / prev.total_sip_amount) * 100 as yoy_growth_pct
FROM sip_yearly curr
LEFT JOIN sip_yearly prev ON curr.calendar_year = prev.calendar_year + 1;

-- 4. Total Gross Transaction Inflow Volume Distributed by Geographic State
SELECT state, COUNT(*) as txn_count, SUM(amount) as total_volume
FROM fact_transactions
GROUP BY state
ORDER BY total_volume DESC;

-- 5. Low-Cost Mutual Funds with Expense Ratios Under 1.0%
SELECT f.scheme_name, f.fund_house, p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 0.01
ORDER BY p.expense_ratio ASC;

-- 6. Total Capital Redemption Drain Volume by Individual Fund House
SELECT f.fund_house, SUM(t.amount) as total_redemption_outflow
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
WHERE t.transaction_type = 'Redemption'
GROUP BY f.fund_house;

-- 7. Allocation Volume Distribution Based on Investor KYC Clearance Status
SELECT kyc_status, COUNT(*) as total_txns, SUM(amount) as combined_value
FROM fact_transactions
GROUP BY kyc_status;

-- 8. Scheme Performance Metrics Matched with Fund Risk Categories
SELECT f.scheme_name, f.risk_grade, p.return_3y, p.return_5y
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3y DESC;

-- 9. Monthly Net Inflow Volatility (Inflows minus Liquidations/Redemptions)
SELECT d.calendar_year, d.month_name,
       SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount ELSE 0 END) - 
       SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount ELSE 0 END) as net_inflow
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_key
GROUP BY d.calendar_year, d.calendar_month;

-- 10. Top 3 Highest Performing Large-Cap Schemes Based on 5-Year Return Windows
SELECT f.scheme_name, f.sub_category, p.return_5y
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.sub_category = 'Large Cap'
ORDER BY p.return_5y DESC
LIMIT 3;
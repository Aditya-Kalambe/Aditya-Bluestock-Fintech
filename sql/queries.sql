-- 1. Count records to verify database integrity
SELECT 'fund_master_count' AS table_name, COUNT(*) FROM fund_master
UNION ALL
SELECT 'nav_history_count' AS table_name, COUNT(*) FROM nav_history;

-- 2. Inspect forward-filled data distribution (Quality metrics audit)
SELECT is_forward_filled, COUNT(*) as record_count 
FROM nav_history 
GROUP BY is_forward_filled;

-- 3. Run a test join checking master tracking completeness
SELECT m.scheme_name, MIN(n.nav_date) as start_date, MAX(n.nav_date) as end_date, COUNT(*) as tracking_days
FROM fund_master m
JOIN nav_history n ON m.scheme_code = n.scheme_code
GROUP BY m.scheme_code;
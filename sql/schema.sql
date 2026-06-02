-- Schema design for Mutual Fund Analytics Platform

DROP TABLE IF EXISTS nav_history;
DROP TABLE IF EXISTS fund_master;

-- 1. Fund Master Table
CREATE TABLE fund_master (
    scheme_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    risk_grade TEXT,
    aum_crore REAL
);

-- 2. Cleaned Time-Series NAV History Table
CREATE TABLE nav_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    nav_date DATE NOT NULL,
    nav REAL NOT NULL,
    is_forward_filled INTEGER DEFAULT 0, -- Tracks if date was a weekend/holiday
    FOREIGN KEY (scheme_code) REFERENCES fund_master(scheme_code),
    UNIQUE(scheme_code, nav_date)
);

-- Create indexes for super-fast time-series metrics calculations
CREATE INDEX idx_nav_lookup ON nav_history(scheme_code, nav_date);
-- Production Star Schema for Bluestock Mutual Fund Analytics Platform
PRAGMA foreign_keys = ON;

-- 1. Dimension Tables
CREATE TABLE dim_fund (
    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER UNIQUE NOT NULL,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    risk_grade TEXT NOT NULL
);

CREATE TABLE dim_date (
    date_key TEXT PRIMARY KEY, -- Format: YYYY-MM-DD
    calendar_year INTEGER NOT NULL,
    calendar_month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
);

-- 2. Fact Tables
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    nav_date TEXT NOT NULL,
    nav REAL NOT NULL CHECK (nav > 0),
    is_forward_filled INTEGER DEFAULT 0 CHECK (is_forward_filled IN (0, 1)),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (nav_date) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount REAL NOT NULL CHECK (amount > 0),
    state TEXT NOT NULL,
    kyc_status TEXT NOT NULL CHECK (kyc_status IN ('Verified', 'Pending', 'Failed')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    return_1y REAL,
    return_3y REAL,
    return_5y REAL,
    expense_ratio REAL CHECK (expense_ratio >= 0.001 AND expense_ratio <= 0.025),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    aum_crore REAL NOT NULL CHECK (aum_crore >= 0),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (snapshot_date) REFERENCES dim_date(date_key)
);

-- Optimization Indexes
CREATE INDEX idx_fact_nav_lookup ON fact_nav(amfi_code, nav_date);
CREATE INDEX idx_fact_trans_lookup ON fact_transactions(amfi_code, transaction_date);